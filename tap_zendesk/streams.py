"""Stream type classes for tap-zendesk."""
from __future__ import annotations

import sys
import typing as t
from typing import Any, Iterable
import json
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
    path = "/api/v2/users.json"
    primary_keys = ["id"]
    replication_key = "created_at"
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
        params = super().get_url_params(context, next_page_token)
        params["role"] = "end-user"
        return params