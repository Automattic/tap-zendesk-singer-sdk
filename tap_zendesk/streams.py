"""Stream type classes for tap-zendesk."""
from __future__ import annotations

import sys
import typing as t
from typing import Any, Iterable, Optional
import json
import time
from datetime import datetime, timezone

from singer_sdk import typing as th  # JSON Schema typing helpers
from tap_zendesk.client import ZendeskStream, IncrementalZendeskStream, NonIncrementalZendeskStream
import requests


if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources


# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = importlib_resources.files(__package__) / "schemas"
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class UsersStream(IncrementalZendeskStream):
    name = "users"
    path = "/api/v2/incremental/users/cursor.json"
    primary_keys = ["id"]
    replication_key = "created_at"
    records_jsonpath = "$.users[*]"  # Adjusted to match the correct JSON path for users.
    next_page_token_jsonpath = "$.after_cursor"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
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
        th.Property("photo", th.ObjectType(
            th.Property("thumbnails", th.ArrayType(th.ObjectType(
                th.Property("width", th.IntegerType),
                th.Property("url", th.StringType),
                th.Property("inline", th.BooleanType),
                th.Property("content_url", th.StringType),
                th.Property("content_type", th.StringType),
                th.Property("file_name", th.StringType),
                th.Property("size", th.IntegerType),
                th.Property("mapped_content_url", th.StringType),
                th.Property("id", th.IntegerType),
                th.Property("height", th.IntegerType)
            ))),
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
            th.Property("deleted", th.BooleanType)
        )),
        th.Property("shared", th.BooleanType),
        th.Property("created_at", th.DateTimeType),
        th.Property("suspended", th.BooleanType),
        th.Property("shared_agent", th.BooleanType),
        th.Property("shared_phone_number", th.BooleanType),
        th.Property("user_fields", th.ObjectType(additional_properties=True)),
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
        th.Property("iana_time_zone", th.StringType)
    ).to_dict()


class TicketsStream(IncrementalZendeskStream):
    name = "tickets"
    path = "/api/v2/incremental/tickets/cursor.json"
    primary_keys = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.tickets[*]"
    next_page_token_jsonpath = "$.after_cursor"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
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
        th.Property("via", th.ObjectType(
            th.Property("source", th.ObjectType(
                th.Property("from", th.ObjectType(
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
                    th.Property("channel", th.StringType)
                )),
                th.Property("to", th.ObjectType(
                    th.Property("address", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("brand_id", th.StringType),
                    th.Property("formatted_phone", th.StringType),
                    th.Property("phone", th.StringType),
                    th.Property("profile_url", th.StringType),
                    th.Property("twitter_id", th.StringType),
                    th.Property("username", th.StringType)
                )),
                th.Property("rel", th.StringType)
            )),
            th.Property("channel", th.StringType)
        )),
        th.Property("ticket_form_id", th.IntegerType),
        th.Property("satisfaction_rating", th.ObjectType(
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
            th.Property("comment", th.StringType)
        )),
        th.Property("sharing_agreement_ids", th.ArrayType(th.IntegerType)),
        th.Property("email_cc_ids", th.ArrayType(th.IntegerType)),
        th.Property("forum_topic_id", th.IntegerType)
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        self.logger.debug(f"Creating child context for ticket_id: {record['id']}")
        return {
            "ticket_id": int(record["id"]),
        }


class TicketAuditsStream(ZendeskStream):
    name = "ticket_audits"
    parent_stream_type = TicketsStream
    path = "/api/v2/tickets/{ticket_id}/audits.json"
    primary_keys = ["id"]
    records_jsonpath = "$.audits[*]"
    next_page_token_jsonpath = "$.meta.after_cursor"
    schema = th.PropertiesList(
        th.Property("author_id", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("events", th.ArrayType(th.ObjectType(
            th.Property("attachments", th.ArrayType(th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("size", th.IntegerType),
                th.Property("url", th.StringType),
                th.Property("inline", th.BooleanType),
                th.Property("height", th.IntegerType),
                th.Property("width", th.IntegerType),
                th.Property("content_url", th.StringType),
                th.Property("mapped_content_url", th.StringType),
                th.Property("content_type", th.StringType),
                th.Property("file_name", th.StringType),
                th.Property("thumbnails", th.ArrayType(th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("size", th.IntegerType),
                    th.Property("url", th.StringType),
                    th.Property("inline", th.BooleanType),
                    th.Property("height", th.IntegerType),
                    th.Property("width", th.IntegerType),
                    th.Property("content_url", th.StringType),
                    th.Property("mapped_content_url", th.StringType),
                    th.Property("content_type", th.StringType),
                    th.Property("file_name", th.StringType)
                )))
            ))),
            th.Property("created_at", th.DateTimeType),
            th.Property("data", th.ObjectType(
                th.Property("transcription_status", th.StringType),
                th.Property("transcription_text", th.StringType),
                th.Property("to", th.StringType),
                th.Property("call_duration", th.StringType),
                th.Property("answered_by_name", th.StringType),
                th.Property("recording_url", th.StringType),
                th.Property("started_at", th.DateTimeType),
                th.Property("answered_by_id", th.IntegerType),
                th.Property("from", th.StringType)
            )),
            th.Property("formatted_from", th.StringType),
            th.Property("formatted_to", th.StringType),
            th.Property("transcription_visible", th.BooleanType),
            th.Property("trusted", th.BooleanType),
            th.Property("html_body", th.StringType),
            th.Property("subject", th.StringType),
            th.Property("field_name", th.StringType),
            th.Property("audit_id", th.IntegerType),
            th.Property("author_id", th.IntegerType),
            th.Property("via", th.ObjectType(
                th.Property("channel", th.StringType),
                th.Property("source", th.ObjectType(
                    th.Property("to", th.ObjectType(
                        th.Property("address", th.StringType),
                        th.Property("name", th.StringType)
                    )),
                    th.Property("from", th.ObjectType(
                        th.Property("title", th.StringType),
                        th.Property("address", th.StringType),
                        th.Property("subject", th.StringType),
                        th.Property("deleted", th.BooleanType),
                        th.Property("name", th.StringType),
                        th.Property("original_recipients", th.ArrayType(th.StringType)),
                        th.Property("id", th.IntegerType),
                        th.Property("ticket_id", th.IntegerType),
                        th.Property("revision_id", th.IntegerType)
                    )),
                    th.Property("rel", th.StringType)
                ))
            )),
            th.Property("type", th.StringType),
            th.Property("macro_id", th.StringType),
            th.Property("body", th.OneOf(
                th.StringType,
                th.ArrayType(
                    th.ObjectType(
                        th.Property("article", th.ObjectType(
                            th.Property("article_id", th.IntegerType, nullable=True),
                            th.Property("brand_id", th.IntegerType, nullable=True),
                            th.Property("locale", th.StringType, nullable=True),
                            th.Property("score", th.NumberType, nullable=True),
                            th.Property("title", th.StringType, nullable=True),
                            th.Property("url", th.StringType, nullable=True),
                            th.Property("html_url", th.StringType, nullable=True),
                            th.Property("id", th.IntegerType, nullable=True)
                        )),
                        th.Property("reviews", th.ObjectType(
                            th.Property("enduser", th.StringType, nullable=True),
                            th.Property("agent", th.ArrayType(th.StringType), nullable=True)
                        )),
                        th.Property("viewed", th.BooleanType, nullable=True)
                    )
                )
            ), nullable=True),
            th.Property("recipients", th.ArrayType(th.IntegerType)),
            th.Property("macro_deleted", th.BooleanType),
            th.Property("plain_body", th.StringType),
            th.Property("id", th.IntegerType),
            th.Property("macro_title", th.StringType),
            th.Property("public", th.BooleanType),
            th.Property("resource", th.StringType)
        ))),
        th.Property("id", th.IntegerType),
        th.Property("metadata", th.ObjectType(
            th.Property("trusted", th.BooleanType),
            th.Property("notifications_suppressed_for", th.ArrayType(th.IntegerType)),
            th.Property("flags_options", th.ObjectType(
                th.Property("2", th.ObjectType(
                    th.Property("trusted", th.BooleanType)
                )),
                th.Property("11", th.ObjectType(
                    th.Property("trusted", th.BooleanType),
                    th.Property("message", th.ObjectType(
                        th.Property("user", th.StringType)
                    ))
                ))
            )),
            th.Property("flags", th.ArrayType(th.IntegerType)),
            th.Property("system", th.ObjectType(
                th.Property("location", th.StringType),
                th.Property("longitude", th.NumberType),
                th.Property("message_id", th.StringType),
                th.Property("raw_email_identifier", th.StringType),
                th.Property("ip_address", th.StringType),
                th.Property("json_email_identifier", th.StringType),
                th.Property("client", th.StringType),
                th.Property("latitude", th.NumberType)
            ))
        )),
        th.Property("ticket_id", th.IntegerType),
        th.Property("via", th.ObjectType(
            th.Property("channel", th.StringType),
            th.Property("source", th.ObjectType(
                th.Property("from", th.ObjectType(
                    th.Property("ticket_ids", th.ArrayType(th.IntegerType)),
                    th.Property("subject", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("address", th.StringType),
                    th.Property("original_recipients", th.ArrayType(th.StringType)),
                    th.Property("id", th.IntegerType),
                    th.Property("ticket_id", th.IntegerType),
                    th.Property("deleted", th.BooleanType),
                    th.Property("title", th.StringType)
                )),
                th.Property("to", th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("address", th.StringType)
                )),
                th.Property("rel", th.StringType)
            ))
        )),
    ).to_dict()


class TicketCommentsStream(ZendeskStream):
    name = "ticket_comments"
    parent_stream_type = TicketsStream
    path = "/api/v2/tickets/{ticket_id}/comments.json"
    primary_keys = ["id"]
    records_jsonpath = "$.comments[*]"
    next_page_token_jsonpath = "$.meta.after_cursor"
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
        th.Property("via", th.ObjectType(
            th.Property("channel", th.StringType),
            th.Property("source", th.ObjectType(
                th.Property("from", th.ObjectType(
                    th.Property("ticket_ids", th.ArrayType(th.IntegerType)),
                    th.Property("subject", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("address", th.StringType),
                    th.Property("original_recipients", th.ArrayType(th.StringType)),
                    th.Property("id", th.IntegerType),
                    th.Property("ticket_id", th.IntegerType),
                    th.Property("deleted", th.BooleanType),
                    th.Property("title", th.StringType)
                )),
                th.Property("to", th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("address", th.StringType)
                )),
                th.Property("rel", th.StringType)
            )),
        )),
        th.Property("metadata", th.ObjectType(
            th.Property("custom", th.ObjectType(additional_properties=True)),
            th.Property("trusted", th.BooleanType),
            th.Property("notifications_suppressed_for", th.ArrayType(th.IntegerType)),
            th.Property("flags_options", th.ObjectType(
                th.Property("2", th.ObjectType(
                    th.Property("trusted", th.BooleanType)
                )),
                th.Property("11", th.ObjectType(
                    th.Property("trusted", th.BooleanType),
                    th.Property("message", th.ObjectType(
                        th.Property("user", th.StringType)
                    ))
                ))
            )),
            th.Property("flags", th.ArrayType(th.IntegerType)),
            th.Property("system", th.ObjectType(
                th.Property("location", th.StringType),
                th.Property("longitude", th.NumberType),
                th.Property("message_id", th.StringType),
                th.Property("raw_email_identifier", th.StringType),
                th.Property("ip_address", th.StringType),
                th.Property("json_email_identifier", th.StringType),
                th.Property("client", th.StringType),
                th.Property("latitude", th.NumberType)
            ))
        )),
        th.Property("attachments", th.ArrayType(th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("size", th.IntegerType),
            th.Property("url", th.StringType),
            th.Property("inline", th.BooleanType),
            th.Property("height", th.IntegerType),
            th.Property("width", th.IntegerType),
            th.Property("content_url", th.StringType),
            th.Property("mapped_content_url", th.StringType),
            th.Property("content_type", th.StringType),
            th.Property("file_name", th.StringType),
            th.Property("thumbnails", th.ArrayType(th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("size", th.IntegerType),
                th.Property("url", th.StringType),
                th.Property("inline", th.BooleanType),
                th.Property("height", th.IntegerType),
                th.Property("width", th.IntegerType),
                th.Property("content_url", th.StringType),
                th.Property("mapped_content_url", th.StringType),
                th.Property("content_type", th.StringType),
                th.Property("file_name", th.StringType)
            )))
        )))
    ).to_dict()


class TicketMetricsStream(ZendeskStream):
    name = "ticket_metrics"
    parent_stream_type = TicketsStream
    path = "/api/v2/tickets/{ticket_id}/metrics.json"
    primary_keys = ["id"]
    records_jsonpath = "$.ticket_metric[*]"
    next_page_token_jsonpath = "$.meta.after_cursor"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("metric", th.StringType),
        th.Property("instance_id", th.IntegerType),
        th.Property("type", th.StringType),
        th.Property("time", th.StringType),
        th.Property("agent_wait_time_in_minutes", th.ObjectType(
            th.Property("calendar", th.IntegerType),
            th.Property("business", th.IntegerType),
        )),
        th.Property("assignee_stations", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("first_resolution_time_in_minutes", th.ObjectType(
            th.Property("calendar", th.IntegerType),
            th.Property("business", th.IntegerType),
        )),
        th.Property("full_resolution_time_in_minutes", th.ObjectType(
            th.Property("calendar", th.IntegerType),
            th.Property("business", th.IntegerType),
        )),
        th.Property("group_stations", th.IntegerType),
        th.Property("latest_comment_added_at", th.DateTimeType),
        th.Property("on_hold_time_in_minutes", th.ObjectType(
            th.Property("calendar", th.IntegerType),
            th.Property("business", th.IntegerType),
        )),
        th.Property("reopens", th.IntegerType),
        th.Property("replies", th.IntegerType),
        th.Property("reply_time_in_minutes", th.ObjectType(
            th.Property("calendar", th.IntegerType),
            th.Property("business", th.IntegerType),
        )),
        th.Property("reply_time_in_seconds", th.ObjectType(
            th.Property("calendar", th.IntegerType),
        )),
        th.Property("requester_updated_at", th.DateTimeType),
        th.Property("requester_wait_time_in_minutes", th.ObjectType(
            th.Property("calendar", th.IntegerType),
            th.Property("business", th.IntegerType),
        )),
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
    next_page_token_jsonpath = "$.meta.after_cursor"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("metric", th.StringType),
        th.Property("instance_id", th.IntegerType),
        th.Property("type", th.StringType),
        th.Property("time", th.StringType),
        th.Property("sla", th.ObjectType(
            th.Property("target", th.IntegerType),
            th.Property("business_hours", th.BooleanType),
            th.Property("policy", th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("title", th.StringType),
                th.Property("description", th.StringType)
            )),
        )),
        th.Property("status", th.ObjectType(
            th.Property("calendar", th.IntegerType),
            th.Property("business", th.IntegerType),
        )),
        th.Property("deleted", th.BooleanType),
    ).to_dict()


class TagsStream(NonIncrementalZendeskStream):
    name = "tags"
    path = "/api/v2/tags.json"
    pagination_size = 1000
    primary_keys = ["name"]
    records_jsonpath = "$.tags[*]"
    next_page_token_jsonpath = "$.meta.after_cursor"
    schema = th.PropertiesList(
        th.Property("count", th.IntegerType),
        th.Property("name", th.StringType),
    ).to_dict()


class SatisfactionRatingsStream(NonIncrementalZendeskStream):
    name = "satisfaction_ratings"
    path = "/api/v2/satisfaction_ratings.json"
    pagination_size = 100
    primary_keys = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.satisfaction_ratings[*]"
    next_page_token_jsonpath = "$.meta.after_cursor"
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
        th.Property("comment", th.StringType)
    ).to_dict()

    def get_url_params(
            self,
            context: dict | None,
            next_page_token: Any | None,
    ) -> dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        end_date = datetime.fromisoformat(self.config.get('end_date'))
        params.update({"end_time": int(end_date.timestamp())})
        params.update({"start_time": self.get_start_time(context)})

        if next_page_token:
            params["page[after]"] = next_page_token
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
        th.Property("filter", th.ObjectType(
            th.Property("all", th.ArrayType(th.ObjectType(
                th.Property("field", th.StringType),
                th.Property("operator", th.StringType),
                th.Property("value", th.OneOf(th.StringType, th.IntegerType))
            ))),
            th.Property("any", th.ArrayType(th.ObjectType(
                th.Property("field", th.StringType),
                th.Property("operator", th.StringType),
                th.Property("value", th.OneOf(th.StringType, th.IntegerType))
            )))
        )),
        th.Property("policy_metrics", th.ArrayType(th.ObjectType(
            th.Property("priority", th.StringType),
            th.Property("target", th.IntegerType),
            th.Property("business_hours", th.BooleanType),
            th.Property("metric", th.StringType)
        ))),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()