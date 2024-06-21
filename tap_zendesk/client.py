"""REST client handling, including ZendeskStream base class."""

from __future__ import annotations

import sys
from typing import Any, Callable, Iterable, Optional, Dict

import json
import time
from datetime import datetime, timezone

import requests
from singer_sdk.authenticators import BasicAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import JSONPathPaginator
from singer_sdk.streams import RESTStream
from requests import Response, PreparedRequest
from time import sleep

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = importlib_resources.files(__package__) / "schemas"


class ZendeskStream(RESTStream):
    """Zendesk stream class."""
    def __init__(self, tap, name=None, schema=None, path=None):
        super().__init__(tap, name, schema, path)
        self.allow_redirects = False
        self.min_remain_rate_limit = int(self.config["min_remain_rate_limit"])

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        subdomain = self.config.get("subdomain", "")
        self.logger.debug(f'subdomain: {subdomain}')
        return f"https://{subdomain}.zendesk.com"

    @property
    def authenticator(self) -> BasicAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        email = self.config.get("email", "")
        api_token = self.config.get("api_token", "")
        return BasicAuthenticator.create_for_stream(
            self,
            username=f"{email}/token",
            password=api_token
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
        if replication_key_value:
            # Parse the string to a datetime object
            record_date = datetime.fromisoformat(replication_key_value)
            start_time = int(record_date.timestamp())
        else:
            start_time = int(time.time()) - 86400  # 24 hours ago as a default
        return start_time

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        if not response.content:
            raise ValueError(f"Received empty response for URL: {response.url}")

        response_json = response.json()
        end_date_str = self.config.get("end_date")
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        if end_date and end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        replication_key = self.replication_key

        for record in extract_jsonpath(self.records_jsonpath, input=response_json):
            if not record:
                self.logger.error("Received empty record")
                continue

            record_date_str = record.get(replication_key)
            if record_date_str:
                record_date = datetime.fromisoformat(record_date_str)
                if record_date.tzinfo is None:
                    record_date = record_date.replace(tzinfo=timezone.utc)
                if end_date and record_date > end_date:
                    self.logger.info(
                        f"Stopping data fetch as record date {record_date} exceeds end date {end_date}")
                    return

            yield record

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

    def _request(
        self,
        prepared_request: PreparedRequest,
        context: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Send a HTTP request with rate limiting.

        Args:
            prepared_request: The prepared HTTP request.
            context: Stream partition or context dictionary.

        Returns:
            The HTTP response object.
        """

        response = self.requests_session.send(
            prepared_request,
            timeout=self.timeout,
            allow_redirects=self.allow_redirects,
        )

        self.last_request_time = time.time()

        self._write_request_duration_log(
            endpoint=self.path,
            response=response,
            context=context,
            extra_tags={"url": prepared_request.path_url}
            if self._LOG_REQUEST_METRIC_URLS
            else None,
        )

        # Check for 404 Not Found and log a warning
        if response.status_code == 404 or response.status_code == 400:
            raise Exception(f"Received {response.status_code} for URL: {response.url}")

        # Rate throttling check
        self.check_rate_throttling(response)

        self.validate_response(response)
        self.logger.debug("Response received successfully.")
        return response


class IncrementalZendeskStream(ZendeskStream):
    pagination_size = 1000

    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = {"per_page": self.pagination_size}
        if next_page_token:
            params["cursor"] = next_page_token
        else:
            params["start_time"] = self.get_start_time(context)
        return params


class NonIncrementalZendeskStream(ZendeskStream):
    pagination_size = 100

    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {"page[size]": self.pagination_size}
        if next_page_token:
            params["page[after]"] = next_page_token
        return params
