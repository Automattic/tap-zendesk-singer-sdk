"""REST client handling, including ZendeskStream base class."""

from __future__ import annotations

from datetime import datetime, timezone
from time import sleep
from typing import Any, Callable, Iterable
from urllib.parse import parse_qsl

import requests
from requests import Response
from singer_sdk.authenticators import BasicAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]

class ZendeskStream(RESTStream):
    """Zendesk stream class."""
    def __init__(self, tap, name=None, schema=None, path=None):
        super().__init__(tap, name, schema, path)
        self.allow_redirects = False
        self.min_remain_rate_limit = self.config.get("min_remain_rate_limit", None)

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return f"https://{self.config['subdomain']}.zendesk.com"

    @property
    def authenticator(self) -> BasicAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BasicAuthenticator(
            self,
            username=f"{self.config['email']}/token",
            password=self.config['api_token']
        )

    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["page[after]"] = next_page_token
        return params

    def get_start_time(self, context: dict | None) -> int:
        """Get the start time for the initial incremental export."""
        replication_key_value = self.get_starting_replication_key_value(context)
        # Parse the string to a datetime object
        record_date = datetime.fromisoformat(replication_key_value)
        start_time = int(record_date.timestamp())
        return start_time

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        if not response.content:
            raise ValueError(f"Received empty response for URL: {response.url}")

        end_date = datetime.fromisoformat(self.config.get("end_date")) if self.config.get("end_date") else None

        if end_date and end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            if not record:
                self.logger.error("Received empty record")
                continue

            if self._does_record_date_exceed_end_date(record, self.replication_key, end_date):
                return

            yield record

    def _does_record_date_exceed_end_date(self, record: dict, replication_key: str, end_date: datetime) -> bool:
        """Check if the record date exceeds the end date."""
        if end_date:
            record_date_str = record.get(replication_key)
            if record_date_str:
                record_date = datetime.fromisoformat(record_date_str)
                if record_date.tzinfo is None:
                    record_date = record_date.replace(tzinfo=timezone.utc)
                if record_date > end_date:
                    self.logger.info(
                        f"Stopping data fetch as record date {record_date} exceeds end date {end_date}")
                    return True
        return False

    def check_rate_throttling(self, response):
        """
        Handle the Zendesk API only allowing 700 API calls per minute.
        """
        if not self.min_remain_rate_limit:
            return

        headers = response.headers
        rate_limit_remain = int(headers.get('x-rate-limit-remaining', headers.get('ratelimit-remaining', 0)))
        rate_limit = int(headers.get('x-rate-limit', headers.get('ratelimit-limit', 0)))
        rate_limit_resets_in_s = headers.get('rate-limit-reset', headers.get('ratelimit-reset'))

        self.logger.debug(f"Remaining rate limit: {rate_limit_remain}/{rate_limit}" +
                          (f" (reset in {rate_limit_resets_in_s}s)" if rate_limit_resets_in_s else " (no reset time)"))

        if rate_limit_remain <= self.min_remain_rate_limit:
            seconds_to_sleep = int(rate_limit_resets_in_s) if rate_limit_resets_in_s else 60
            self.logger.warning(f"API rate limit exceeded (rate limit: {rate_limit}, remain: {rate_limit_remain}, "
                                f"min remain limit: {self.min_remain_rate_limit}). "
                                f"Tap will retry the data collection after {seconds_to_sleep} seconds.")
            sleep(seconds_to_sleep)

    def validate_response(self, response: requests.Response) -> None:
        # Check for 404 Not Found and log a warning
        if response.status_code == 404 or response.status_code == 400:
            raise Exception(f"Received {response.status_code} for URL: {response.url}")

        self.check_rate_throttling(response)
        super().validate_response(response)


class IncrementalPaginator(BaseHATEOASPaginator):
    def get_next_url(self, response: Response) -> str:
        raise NotImplementedError()

    def has_more(self, response: Response) -> bool:
        return not bool(response.json().get("end_of_stream"))


class IncrementalCursorBasedPaginator(IncrementalPaginator):
    def get_next_url(self, response: Response) -> str:
        return response.json().get("after_url")


class IncrementalTimeBasedPaginator(IncrementalPaginator):
    def get_next_url(self, response: Response) -> str:
        return response.json().get("next_page")


class IncrementalZendeskStream(ZendeskStream):
    pagination_size = 1000

    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        if next_page_token:
            return dict(parse_qsl(next_page_token.query))
        return {
            "per_page": self.pagination_size,
            "start_time": self.get_start_time(context)
        }

    def get_new_paginator(self):
        return IncrementalCursorBasedPaginator() if 'cursor.json' in self.path else IncrementalTimeBasedPaginator()


class CursorPaginator(BaseHATEOASPaginator):
    def get_next_url(self, response: Response) -> str:
        return response.json().get("links", {}).get("next", {})


class NonIncrementalZendeskStream(ZendeskStream):
    pagination_size = 100

    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        if next_page_token:
            return dict(parse_qsl(next_page_token.query))
        if self.pagination_size:
            return {"page[size]": self.pagination_size}
        return {}

    def get_new_paginator(self):
        return CursorPaginator()
