"""Zendesk tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_zendesk import streams


class TapZendesk(Tap):
    """Zendesk tap class."""

    name = "tap-zendesk"

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
        th.Property(
            "end_date",
            th.DateTimeType,
            description="The latest record date to sync",
        ),
        th.Property(
            "min_remain_rate_limit",
            th.IntegerType,
            description="Sets a limit to the remain rate that the tap will not will not overtake (it will wait for the reset)",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.ZendeskStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.SlaPoliciesStream(self),
            streams.SatisfactionRatingsStream(self),
            streams.TagsStream(self),
            streams.TicketsStream(self),
            streams.TicketsSideloadingStream(self),
            streams.TicketEventsStream(self),
            streams.TicketAuditsStream(self),
            streams.TicketCommentsStream(self),
            streams.TicketMetricsStream(self),
            streams.TicketMetricEventsStream(self),
            streams.UsersStream(self),
            streams.GroupsStream(self),
        ]


if __name__ == "__main__":
    TapZendesk.cli()
