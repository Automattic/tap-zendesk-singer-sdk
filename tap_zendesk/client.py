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
        self.last_request_time = 0  # Initialize last_request_time
        self.allow_redirects = False

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

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {"page[size]": 100, "sort_order": "asc"}  # Include sort_order
        if next_page_token:
            params["page[after]"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        if not response.content:
            self.logger.warning("Received empty response for URL: %s", response.url)
            return

        try:
            response_json = response.json()
            self.logger.debug(f"Response JSON: {response_json}")
        except json.JSONDecodeError:
            self.logger.error("Unable to decode JSON response: %s", response.text)
            return

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
        # Calculate the time difference between the current time and the last request time
        time_since_last_request = time.time() - self.last_request_time

        # Ensure we don't exceed 250 requests per minute (1 request per 0.24 seconds)
        if time_since_last_request < 0.24:
            time.sleep(0.24 - time_since_last_request)

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
        if response.status_code == 404:
            self.logger.warning(f"Received 404 for URL: {response.url}")
            return None

        self.validate_response(response)
        self.logger.debug("Response received successfully.")
        return response

    def is_end_of_stream(self, response):
        """Determine if the end of stream has been reached."""
        if 'end_of_stream' in response.json():
            end_of_stream = response.json().get('end_of_stream')
            self.logger.debug(f"End of stream: {end_of_stream}")
            return end_of_stream
        end_of_stream = not response.json().get('meta', {}).get('after_cursor')
        self.logger.debug(f"End of stream (meta): {end_of_stream}")
        return end_of_stream

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        return row


class IncrementalZendeskStream(ZendeskStream):
    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = {"per_page": 1000}
        if next_page_token:
            params["cursor"] = next_page_token
        else:
            start_time = self.get_start_time(context)
            params["start_time"] = start_time
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


class NonIncrementalZendeskStream(ZendeskStream):
    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {"page[size]": 100, "sort_order": "asc"}  # Include sort_order
        if next_page_token:
            params["page[after]"] = next_page_token
        return params
