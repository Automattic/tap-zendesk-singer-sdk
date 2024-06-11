"""Stream type classes for tap-zendesk."""
from __future__ import annotations

import sys
import typing as t
from typing import Any, Iterable
import json
import time
from datetime import datetime, timezone

from singer_sdk import typing as th  # JSON Schema typing helpers
from tap_zendesk.client import ZendeskStream
import requests


if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources


# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = importlib_resources.files(__package__) / "schemas"
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class UsersStream(ZendeskStream):
    name = "users"
    path = "/api/v2/incremental/users/cursor.json"
    primary_keys = ["id"]
    replication_key = "created_at"
    records_jsonpath = "$.users[*]"  # Adjusted to match the correct JSON path for users.
    next_page_token_jsonpath = "$.meta.after_cursor"
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


class TicketsStream(ZendeskStream):
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


class TagsStream(ZendeskStream):
    name = "tags"
    path = "/api/v2/tags.json"
    primary_keys = ["name"]
    records_jsonpath = "$.tags[*]"
    next_page_token_jsonpath = "$.meta.after_cursor"
    schema = th.PropertiesList(
        th.Property("count", th.IntegerType),
        th.Property("name", th.StringType),
    ).to_dict()


class SatisfactionRatingsStream(ZendeskStream):
    name = "satisfaction_ratings"
    path = "/api/v2/satisfaction_ratings.json"
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
