from singer_sdk import typing as th


EXPLODED_ANY_TYPE = th.CustomType(
    {
        'type': ['string', 'object', 'array', 'boolean', 'number', 'null'],
        'items': {'type': ['string', 'object', 'number', 'null']},
    }
)


SYSTEM_PROPERTY = th.Property(
    "system",
    th.ObjectType(
        th.Property("location", th.StringType),
        th.Property("longitude", th.NumberType),
        th.Property("message_id", th.StringType),
        th.Property("raw_email_identifier", th.StringType),
        th.Property("ip_address", th.StringType),
        th.Property("json_email_identifier", th.StringType),
        th.Property("client", th.StringType),
        th.Property("latitude", th.NumberType),
    ),
)

FLAGS_OPTIONS_PROPERTY = th.Property(
    "flags_options",
    th.ObjectType(
        th.Property("2", th.ObjectType(th.Property("trusted", th.BooleanType))),
        th.Property(
            "11",
            th.ObjectType(
                th.Property("trusted", th.BooleanType),
                th.Property(
                    "message", th.ObjectType(th.Property("user", th.StringType))
                ),
            ),
        ),
    ),
)
