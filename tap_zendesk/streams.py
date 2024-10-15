"""Stream type classes for tap-zendesk."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

from singer_sdk import typing as th

from tap_zendesk.client import (
    ZendeskStream,
    IncrementalZendeskStream,
    NonIncrementalZendeskStream,
)
from tap_zendesk.helpers.schema import (
    ATTACHMENTS_PROPERTY,
    METADATA_PROPERTY,
    EXPLODED_ANY_TYPE,
)


class GroupsStream(NonIncrementalZendeskStream):
    name = "groups"
    path = "/api/v2/groups.json?exclude_deleted=false"
    primary_keys = ["id"]
    records_jsonpath = "$.groups[*]"
    schema = th.PropertiesList(
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("name", th.StringType),
        th.Property("id", th.IntegerType),
        th.Property("default", th.BooleanType),
        th.Property("deleted", th.BooleanType),
        th.Property("is_public", th.BooleanType),
        th.Property("description", th.StringType),
        th.Property("url", th.StringType),
    ).to_dict()


class OrganizationsStream(IncrementalZendeskStream):
    name = "organizations"
    path = "/api/v2/incremental/organizations"
    primary_keys = ["id"]
    records_jsonpath = "$.organizations[*]"
    replication_key = "updated_at"
    schema = th.PropertiesList(
        th.Property("created_at", th.DateTimeType),
        th.Property("details", th.StringType),
        th.Property("domain_names", th.ArrayType(th.StringType)),
        th.Property("group_id", th.IntegerType),
        th.Property("id", th.IntegerType),
        th.Property("external_id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("notes", th.StringType),
        th.Property("organization_fields", th.CustomType({"type": ["object", "null"]})),
        th.Property("shared_comments", th.BooleanType),
        th.Property("shared_tickets", th.BooleanType),
        th.Property("tags", th.ArrayType(th.StringType)),
        th.Property("updated_at", th.DateTimeType),
        th.Property("url", th.StringType),
    ).to_dict()


class UsersStream(IncrementalZendeskStream):
    name = "users"
    path = "/api/v2/incremental/users/cursor.json"
    primary_keys = ["id"]
    replication_key = "updated_at"
    records_jsonpath = (
        "$.users[*]"  # Adjusted to match the correct JSON path for users.
    )
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("custom_status_id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("verified", th.BooleanType),
        th.Property("role", th.StringType),
        th.Property("tags", th.ArrayType(th.StringType)),
        th.Property("chat_only", th.BooleanType),
        th.Property("role_type", th.IntegerType),
        th.Property("phone", th.StringType),
        th.Property("organization_id", th.IntegerType),
        th.Property("details", th.StringType),
        th.Property("email", th.StringType),
        th.Property("only_private_comments", th.BooleanType),
        th.Property("signature", th.StringType),
        th.Property("restricted_agent", th.BooleanType),
        th.Property("moderator", th.BooleanType),
        th.Property("external_id", th.StringType),
        th.Property("time_zone", th.StringType),
        th.Property(
            "photo",
            th.ObjectType(
                th.Property(
                    "thumbnails",
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("width", th.IntegerType),
                            th.Property("url", th.StringType),
                            th.Property("inline", th.BooleanType),
                            th.Property("content_url", th.StringType),
                            th.Property("content_type", th.StringType),
                            th.Property("file_name", th.StringType),
                            th.Property("size", th.IntegerType),
                            th.Property("mapped_content_url", th.StringType),
                            th.Property("id", th.IntegerType),
                            th.Property("height", th.IntegerType),
                            th.Property("deleted", th.BooleanType),
                        )
                    ),
                ),
                th.Property("width", th.IntegerType),
                th.Property("url", th.StringType),
                th.Property("inline", th.BooleanType),
                th.Property("content_url", th.StringType),
                th.Property("content_type", th.StringType),
                th.Property("file_name", th.StringType),
                th.Property("size", th.IntegerType),
                th.Property("mapped_content_url", th.StringType),
                th.Property("id", th.IntegerType),
                th.Property("height", th.IntegerType),
                th.Property("deleted", th.BooleanType),
            ),
        ),
        th.Property("shared", th.BooleanType),
        th.Property("created_at", th.DateTimeType),
        th.Property("suspended", th.BooleanType),
        th.Property("shared_agent", th.BooleanType),
        th.Property("shared_phone_number", th.BooleanType),
        th.Property("user_fields", th.CustomType({"type": ["object", "null"]})),
        th.Property("last_login_at", th.DateTimeType),
        th.Property("alias", th.StringType),
        th.Property("two_factor_auth_enabled", th.BooleanType),
        th.Property("notes", th.StringType),
        th.Property("default_group_id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("permanently_deleted", th.BooleanType),
        th.Property("locale_id", th.IntegerType),
        th.Property("custom_role_id", th.IntegerType),
        th.Property("ticket_restriction", th.StringType),
        th.Property("locale", th.StringType),
        th.Property("report_csv", th.BooleanType),
        th.Property("iana_time_zone", th.StringType),
    ).to_dict()


TICKET_SCHEMA = (
    th.Property("id", th.IntegerType),
    th.Property("custom_status_id", th.IntegerType),
    th.Property("organization_id", th.IntegerType),
    th.Property("requester_id", th.IntegerType),
    th.Property("problem_id", th.IntegerType),
    th.Property("is_public", th.BooleanType),
    th.Property("description", th.StringType),
    th.Property("follower_ids", th.ArrayType(th.IntegerType)),
    th.Property("submitter_id", th.IntegerType),
    th.Property("generated_timestamp", th.IntegerType),
    th.Property("brand_id", th.IntegerType),
    th.Property("group_id", th.IntegerType),
    th.Property("type", th.StringType),
    th.Property("recipient", th.StringType),
    th.Property("collaborator_ids", th.ArrayType(th.IntegerType)),
    th.Property("tags", th.ArrayType(th.StringType)),
    th.Property("has_incidents", th.BooleanType),
    th.Property("created_at", th.DateTimeType),
    th.Property("raw_subject", th.StringType),
    th.Property("status", th.StringType),
    th.Property("updated_at", th.DateTimeType),
    th.Property("url", th.StringType),
    th.Property("allow_channelback", th.BooleanType),
    th.Property("allow_attachments", th.BooleanType),
    th.Property("due_at", th.DateTimeType),
    th.Property("followup_ids", th.ArrayType(th.IntegerType)),
    th.Property("priority", th.StringType),
    th.Property("assignee_id", th.IntegerType),
    th.Property("subject", th.StringType),
    th.Property("external_id", th.StringType),
    th.Property(
        "via",
        th.ObjectType(
            th.Property(
                "source",
                th.ObjectType(
                    th.Property(
                        "from",
                        th.ObjectType(
                            th.Property("name", th.StringType),
                            th.Property("ticket_id", th.IntegerType),
                            th.Property("address", th.StringType),
                            th.Property("subject", th.StringType),
                            th.Property("brand_id", th.StringType),
                            th.Property("formatted_phone", th.StringType),
                            th.Property("phone", th.StringType),
                            th.Property("profile_url", th.StringType),
                            th.Property("twitter_id", th.StringType),
                            th.Property("username", th.StringType),
                            th.Property("channel", th.StringType),
                        ),
                    ),
                    th.Property(
                        "to",
                        th.ObjectType(
                            th.Property("address", th.StringType),
                            th.Property("name", th.StringType),
                            th.Property("brand_id", th.StringType),
                            th.Property("formatted_phone", th.StringType),
                            th.Property("phone", th.StringType),
                            th.Property("profile_url", th.StringType),
                            th.Property("twitter_id", th.StringType),
                            th.Property("username", th.StringType),
                        ),
                    ),
                    th.Property("rel", th.StringType),
                ),
            ),
            th.Property("channel", th.StringType),
        ),
    ),
    th.Property("ticket_form_id", th.IntegerType),
    th.Property(
        "satisfaction_rating",
        th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("assignee_id", th.IntegerType),
            th.Property("group_id", th.IntegerType),
            th.Property("reason_id", th.IntegerType),
            th.Property("requester_id", th.IntegerType),
            th.Property("ticket_id", th.IntegerType),
            th.Property("updated_at", th.DateTimeType),
            th.Property("created_at", th.DateTimeType),
            th.Property("url", th.StringType),
            th.Property("score", th.StringType),
            th.Property("reason", th.StringType),
            th.Property("comment", th.StringType),
        ),
    ),
    th.Property("sharing_agreement_ids", th.ArrayType(th.IntegerType)),
    th.Property("email_cc_ids", th.ArrayType(th.IntegerType)),
    th.Property("forum_topic_id", th.IntegerType),
    th.Property(
        "custom_fields",
        th.ArrayType(
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("value", EXPLODED_ANY_TYPE),
            )
        ),
    ),
    th.Property("from_messaging_channel", th.BooleanType),
)


class TicketsStream(IncrementalZendeskStream):
    name = "tickets"
    path = "/api/v2/incremental/tickets/cursor.json"
    primary_keys = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.tickets[*]"
    schema = th.PropertiesList(*TICKET_SCHEMA).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        self.logger.debug(f"Creating child context for ticket_id: {record['id']}")
        return {
            "ticket_id": int(record["id"]),
        }


class TicketsSideloadingStream(IncrementalZendeskStream):
    name = "tickets_sideloading"
    path = "/api/v2/incremental/tickets/cursor.json?include=metric_events,slas"
    primary_keys = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.tickets[*]"
    schema = th.PropertiesList(
        *TICKET_SCHEMA,
        th.Property("metric_events", th.CustomType({"type": ["object", "null"]})),
        th.Property("slas", th.CustomType({"type": ["object", "null"]})),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        self.logger.debug(f"Creating child context for ticket_id: {record['id']}")
        return {
            "ticket_id": int(record["id"]),
        }


class TicketFieldsStream(NonIncrementalZendeskStream):
    name = "ticket_fields"
    path = "/api/v2/ticket_fields.json"
    primary_keys = ["id"]
    records_jsonpath = "$.ticket_fields[*]"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("position", th.IntegerType),
        th.Property("active", th.BooleanType),
        th.Property("agent_description", th.StringType),
        th.Property("collapsed_for_agents", th.BooleanType),
        th.Property("created_at", th.DateTimeType),
        th.Property("creator_app_name", th.StringType),
        th.Property("creator_user_id", th.IntegerType),
        th.Property("custom_field_options", th.ArrayType(th.AnyType)),
        th.Property("custom_statuses", th.ArrayType(th.AnyType)),
        th.Property("description", th.StringType),
        th.Property("editable_in_portal", th.BooleanType),
        th.Property("raw_description", th.StringType),
        th.Property("raw_title", th.StringType),
        th.Property("raw_title_in_portal", th.StringType),
        th.Property("regexp_for_validation", th.StringType),
        th.Property("relationship_filter", th.CustomType({"type": ["object", "null"]})),
        th.Property("relationship_target_type", th.StringType),
        th.Property("removable", th.BooleanType),
        th.Property("required", th.BooleanType),
        th.Property("required_in_portal", th.BooleanType),
        th.Property("sub_type_id", th.IntegerType),
        th.Property("system_field_options", th.ArrayType(th.AnyType)),
        th.Property("tag", th.StringType),
        th.Property("title", th.StringType),
        th.Property("title_in_portal", th.StringType),
        th.Property("type", th.StringType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("url", th.StringType),
        th.Property("visible_in_portal", th.BooleanType),
    ).to_dict()


class TicketAuditsStream(NonIncrementalZendeskStream):
    name = "ticket_audits"
    parent_stream_type = TicketsStream
    path = "/api/v2/tickets/{ticket_id}/audits.json"
    primary_keys = ["id"]
    records_jsonpath = "$.audits[*]"
    state_partitioning_keys = []
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("author_id", th.IntegerType),
        METADATA_PROPERTY,
        th.Property(
            "events",
            th.ArrayType(
                th.ObjectType(
                    ATTACHMENTS_PROPERTY,
                    th.Property("created_at", th.DateTimeType),
                    th.Property(
                        "data",
                        th.ObjectType(
                            th.Property("transcription_status", th.StringType),
                            th.Property("transcription_text", th.StringType),
                            th.Property("to", th.StringType),
                            th.Property("call_duration", th.StringType),
                            th.Property("answered_by_name", th.StringType),
                            th.Property("recording_url", th.StringType),
                            th.Property("started_at", th.DateTimeType),
                            th.Property("answered_by_id", th.IntegerType),
                            th.Property("from", th.StringType),
                        ),
                    ),
                    th.Property("formatted_from", th.StringType),
                    th.Property("formatted_to", th.StringType),
                    th.Property("transcription_visible", th.BooleanType),
                    th.Property("trusted", th.BooleanType),
                    th.Property("html_body", th.StringType),
                    th.Property("subject", th.StringType),
                    th.Property("field_name", th.StringType),
                    th.Property("audit_id", th.IntegerType),
                    th.Property(
                        "value",
                        th.CustomType(
                            {
                                'type': ['string', 'array', 'object', 'null'],
                                'items': {'type': 'string'},
                            }
                        ),
                    ),
                    th.Property("author_id", th.IntegerType),
                    th.Property(
                        "via",
                        th.ObjectType(
                            th.Property("channel", th.StringType),
                            th.Property(
                                "source",
                                th.ObjectType(
                                    th.Property(
                                        "to",
                                        th.ObjectType(
                                            th.Property("address", th.StringType),
                                            th.Property("name", th.StringType),
                                        ),
                                    ),
                                    th.Property(
                                        "from",
                                        th.ObjectType(
                                            th.Property("title", th.StringType),
                                            th.Property("address", th.StringType),
                                            th.Property("subject", th.StringType),
                                            th.Property("deleted", th.BooleanType),
                                            th.Property("name", th.StringType),
                                            th.Property(
                                                "original_recipients",
                                                th.ArrayType(th.StringType),
                                            ),
                                            th.Property("id", th.IntegerType),
                                            th.Property("ticket_id", th.IntegerType),
                                            th.Property("revision_id", th.IntegerType),
                                        ),
                                    ),
                                    th.Property("rel", th.StringType),
                                ),
                            ),
                        ),
                    ),
                    th.Property("type", th.StringType),
                    th.Property("macro_id", th.StringType),
                    th.Property(
                        "body",
                        th.CustomType({'type': ['string', 'object', 'array', 'null']}),
                    ),
                    th.Property("recipients", th.ArrayType(th.IntegerType)),
                    th.Property("macro_deleted", th.BooleanType),
                    th.Property("plain_body", th.StringType),
                    th.Property("id", th.IntegerType),
                    th.Property(
                        "previous_value",
                        th.CustomType(
                            {
                                'type': ['string', 'array', 'object', 'null'],
                                'items': {'type': 'string'},
                            }
                        ),
                    ),
                    th.Property("macro_title", th.StringType),
                    th.Property("public", th.BooleanType),
                    th.Property("resource", th.StringType),
                )
            ),
        ),
        th.Property(
            "via",
            th.ObjectType(
                th.Property("channel", th.StringType),
                th.Property(
                    "source",
                    th.ObjectType(
                        th.Property(
                            "from",
                            th.ObjectType(
                                th.Property("ticket_ids", th.ArrayType(th.IntegerType)),
                                th.Property("subject", th.StringType),
                                th.Property("name", th.StringType),
                                th.Property("address", th.StringType),
                                th.Property(
                                    "original_recipients", th.ArrayType(th.StringType)
                                ),
                                th.Property("id", th.IntegerType),
                                th.Property("ticket_id", th.IntegerType),
                                th.Property("deleted", th.BooleanType),
                                th.Property("title", th.StringType),
                            ),
                        ),
                        th.Property(
                            "to",
                            th.ObjectType(
                                th.Property("name", th.StringType),
                                th.Property("address", th.StringType),
                            ),
                        ),
                        th.Property("rel", th.StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()


class TicketEventsStream(IncrementalZendeskStream):
    name = "ticket_events"
    path = "/api/v2/incremental/ticket_events.json?include=comment_events"
    primary_keys = ["id"]
    replication_key = "created_at"
    records_jsonpath = "$.ticket_events[*]"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("timestamp", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updater_id", th.IntegerType),
        th.Property("via", th.StringType),
        th.Property("child_events", th.CustomType({"type": ["array", "null"]})),
        th.Property("system", th.CustomType({"type": ["object", "null"]})),
        th.Property("metadata", th.CustomType({"type": ["object", "null"]})),
        th.Property("merged_ticket_ids", th.ArrayType(th.IntegerType)),
        th.Property("event_type", th.StringType),
    ).to_dict()


class TicketCommentsStream(NonIncrementalZendeskStream):
    name = "ticket_comments"
    parent_stream_type = TicketsStream
    path = "/api/v2/tickets/{ticket_id}/comments.json"
    primary_keys = ["id"]
    records_jsonpath = "$.comments[*]"
    state_partitioning_keys = []
    schema = th.PropertiesList(
        th.Property("created_at", th.DateTimeType),
        th.Property("body", th.StringType),
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("type", th.StringType),
        th.Property("html_body", th.StringType),
        th.Property("plain_body", th.StringType),
        th.Property("public", th.BooleanType),
        th.Property("audit_id", th.IntegerType),
        th.Property("author_id", th.IntegerType),
        th.Property(
            "via",
            th.ObjectType(
                th.Property("channel", th.StringType),
                th.Property(
                    "source",
                    th.ObjectType(
                        th.Property(
                            "from",
                            th.ObjectType(
                                th.Property("ticket_ids", th.ArrayType(th.IntegerType)),
                                th.Property("subject", th.StringType),
                                th.Property("name", th.StringType),
                                th.Property("address", th.StringType),
                                th.Property(
                                    "original_recipients", th.ArrayType(th.StringType)
                                ),
                                th.Property("id", th.IntegerType),
                                th.Property("ticket_id", th.IntegerType),
                                th.Property("deleted", th.BooleanType),
                                th.Property("title", th.StringType),
                            ),
                        ),
                        th.Property(
                            "to",
                            th.ObjectType(
                                th.Property("name", th.StringType),
                                th.Property("address", th.StringType),
                            ),
                        ),
                        th.Property("rel", th.StringType),
                    ),
                ),
            ),
        ),
        METADATA_PROPERTY,
        ATTACHMENTS_PROPERTY,
    ).to_dict()


class TicketMetricsStream(NonIncrementalZendeskStream):
    name = "ticket_metrics"
    parent_stream_type = TicketsStream
    path = "/api/v2/tickets/{ticket_id}/metrics.json"
    primary_keys = ["id"]
    records_jsonpath = "$.ticket_metric[*]"
    state_partitioning_keys = []
    pagination_size = None
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("metric", th.StringType),
        th.Property("instance_id", th.IntegerType),
        th.Property("type", th.StringType),
        th.Property("time", th.StringType),
        th.Property(
            "agent_wait_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property("assignee_stations", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property(
            "first_resolution_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property(
            "full_resolution_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property("group_stations", th.IntegerType),
        th.Property("latest_comment_added_at", th.DateTimeType),
        th.Property(
            "on_hold_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property("reopens", th.IntegerType),
        th.Property("replies", th.IntegerType),
        th.Property(
            "reply_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property(
            "reply_time_in_seconds",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
            ),
        ),
        th.Property("requester_updated_at", th.DateTimeType),
        th.Property(
            "requester_wait_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property("status_updated_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("url", th.StringType),
        th.Property("initially_assigned_at", th.DateTimeType),
        th.Property("assigned_at", th.DateTimeType),
        th.Property("solved_at", th.DateTimeType),
        th.Property("assignee_updated_at", th.DateTimeType),
    ).to_dict()


class TicketMetricEventsStream(IncrementalZendeskStream):
    name = "ticket_metric_events"
    path = "/api/v2/incremental/ticket_metric_events.json"
    primary_keys = ["id"]
    replication_key = "time"
    records_jsonpath = "$.ticket_metric_events[*]"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("metric", th.StringType),
        th.Property("instance_id", th.IntegerType),
        th.Property("type", th.StringType),
        th.Property("time", th.DateTimeType),
        th.Property(
            "sla",
            th.ObjectType(
                th.Property("target", th.IntegerType),
                th.Property("business_hours", th.BooleanType),
                th.Property(
                    "policy",
                    th.ObjectType(
                        th.Property("id", th.IntegerType),
                        th.Property("title", th.StringType),
                        th.Property("description", th.StringType),
                    ),
                ),
            ),
        ),
        th.Property(
            "status",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property("deleted", th.BooleanType),
    ).to_dict()


class TagsStream(NonIncrementalZendeskStream):
    name = "tags"
    path = "/api/v2/tags.json"
    pagination_size = 1000
    primary_keys = ["name"]
    records_jsonpath = "$.tags[*]"
    schema = th.PropertiesList(
        th.Property("count", th.IntegerType),
        th.Property("name", th.StringType),
    ).to_dict()


class SatisfactionRatingsStream(NonIncrementalZendeskStream):
    name = "satisfaction_ratings"
    path = "/api/v2/satisfaction_ratings.json"
    primary_keys = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.satisfaction_ratings[*]"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("assignee_id", th.IntegerType),
        th.Property("group_id", th.IntegerType),
        th.Property("reason_id", th.IntegerType),
        th.Property("requester_id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("created_at", th.DateTimeType),
        th.Property("url", th.StringType),
        th.Property("score", th.StringType),
        th.Property("reason", th.StringType),
        th.Property("comment", th.StringType),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        if next_page_token:
            return params

        if 'end_date' in self.config:
            end_date = datetime.fromisoformat(self.config.get('end_date'))
            params.update({"end_time": int(end_date.timestamp())})
        params.update({"start_time": self.get_start_time(context)})
        return params


class SlaPoliciesStream(ZendeskStream):
    name = "sla_policies"
    path = "/api/v2/slas/policies.json"
    primary_keys = ["id"]
    records_jsonpath = "$.sla_policies[*]"
    next_page_token_jsonpath = "$.next_page"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property(
            "filter",
            th.ObjectType(
                th.Property(
                    "all",
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("field", th.StringType),
                            th.Property("operator", th.StringType),
                            th.Property("value", th.AnyType),
                        )
                    ),
                ),
                th.Property(
                    "any",
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("field", th.StringType),
                            th.Property("operator", th.StringType),
                            th.Property("value", th.AnyType),
                        )
                    ),
                ),
            ),
        ),
        th.Property(
            "policy_metrics",
            th.ArrayType(
                th.ObjectType(
                    th.Property("priority", th.StringType),
                    th.Property("metric", th.StringType),
                    th.Property("target", th.IntegerType),
                    th.Property("target_in_seconds", th.IntegerType),
                    th.Property("business_hours", th.BooleanType),
                )
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        if next_page_token:
            params = parse_qs(urlparse(next_page_token).query)
        return params
