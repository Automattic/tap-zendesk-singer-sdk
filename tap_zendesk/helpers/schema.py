from singer_sdk import typing as th


SYSTEM_PROPERTY = th.Property("system", th.ObjectType(
    th.Property("location", th.StringType),
    th.Property("longitude", th.NumberType),
    th.Property("message_id", th.StringType),
    th.Property("raw_email_identifier", th.StringType),
    th.Property("ip_address", th.StringType),
    th.Property("json_email_identifier", th.StringType),
    th.Property("client", th.StringType),
    th.Property("latitude", th.NumberType)
))


ATTACHMENTS_PROPERTY = th.Property("attachments", th.ArrayType(
    th.ObjectType(
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
        th.Property("thumbnails", th.ArrayType(
            th.ObjectType(
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
            )
        ))
    )
))


FLAGS_OPTIONS_PROPERTY = th.Property("flags_options", th.ObjectType(
    th.Property("2", th.ObjectType(
        th.Property("trusted", th.BooleanType)
    )),
    th.Property("11", th.ObjectType(
        th.Property("trusted", th.BooleanType),
        th.Property("message", th.ObjectType(
            th.Property("user", th.StringType)
        ))
    ))
))


METADATA_PROPERTY = th.Property("metadata", th.ObjectType(
    th.Property("custom", th.CustomType({'type': ['string', 'null', 'object']})),
    th.Property("trusted", th.BooleanType),
    th.Property("notifications_suppressed_for", th.ArrayType(th.IntegerType)),
    FLAGS_OPTIONS_PROPERTY,
    th.Property("flags", th.ArrayType(th.IntegerType)),
    SYSTEM_PROPERTY
))
