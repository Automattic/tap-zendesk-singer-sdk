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
        self.logger.info(f'subdomain: {subdomain}')
        return f"https://{subdomain}.zendesk.com"

    records_jsonpath = "$.users[*]"  # Adjusted to match the correct JSON path for users.

    # Set this value or override `get_new_paginator`.
    next_page_token_jsonpath = "$.meta.after_cursor"

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

    def get_new_paginator(self) -> JSONPathPaginator:
        """Create a new pagination helper instance.

        Returns:
            A pagination helper instance.
        """
        return JSONPathPaginator(self.next_page_token_jsonpath)

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

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,  # noqa: ARG002, ANN401
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        return None

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        if not response.content:
            self.logger.warning("Received empty response for URL: %s", response.url)
            return

        try:
            response_json = response.json()
            self.logger.debug(f"Response JSON: {response_json}")
        except json.JSONDecodeError:
            self.logger.error("Unable to decode JSON response: %s", response.text)
            return

        yield from extract_jsonpath(self.records_jsonpath, input=response_json)

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

        self.validate_response(response)
        self.logger.info("Response received successfully.")
        return response

    def get_records(self, context):
        end_date_str = self.config.get("end_date")
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        if end_date and end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        replication_key = self.replication_key

        paginator = self.get_new_paginator()
        next_page_token = None

        while True:
            prepared_request = self.prepare_request(context, next_page_token)
            response = self._request(prepared_request, context)
            if not response:
                self.logger.error("Received empty response")
                break

            records = self.parse_response(response)
            for record in records:
                if not record:
                    self.logger.error("Received empty record")
                    continue

                try:
                    record_json = json.loads(json.dumps(record))
                    #self.logger.info(record_json)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSONDecodeError encountered while parsing record: {e}")
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

            next_page_token = paginator.get_next(response)
            self.logger.info(f"Next page token: {next_page_token}")
            if not next_page_token:
                break

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
