ALLOWED_HOSTS = ["*"]

# https://docs.djangoproject.com/en/4.0/topics/logging/#logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{levelname} {asctime} {module} {filename} {lineno} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        # "root": {
        #     "handlers": ["console"],
        #     "level": "INFO",
        #     "propagate": False,
        # },
    },
}


DJANGO_DATA_SINK_SETTINGS = {
    "partition_prefix": "new_prefix",
    "partition_by": "request_time",  # request_time, response_time in context, and put_time
    "partition_date_format": "%Y-%m-%d",  # default interval day by day
    "app_secret": None,
    "backend": "django_data_sdk.sink.backends.KafkaBackend",
    "backend_kwargs": {},
    "sink_mode": "DIRECT",
}
