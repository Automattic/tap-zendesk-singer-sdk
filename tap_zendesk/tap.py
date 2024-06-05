"""Zendesk tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_zendesk import streams


class TapZendesk(Tap):
    """Zendesk tap class."""

    name = "tap-zendesk"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "subdomain",
            th.StringType,
            required=True,
            description="Project IDs to replicate",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.ZendeskStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.UsersStream(self),
        ]


if __name__ == "__main__":
    TapZendesk.cli()
