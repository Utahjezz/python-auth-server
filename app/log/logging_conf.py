import logging
from typing import Dict

from asgi_correlation_id.log_filters import CorrelationIdFilter

from app.config.settings import Settings


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter out the health check endpoints.

        :param record: The log record to filter.

        :return: True if the record should be logged, False otherwise.
        """
        return (
            record.getMessage().find("/healthz") == -1
            and record.getMessage().find("/docs") == -1
            and record.getMessage().find("/openapi.json") == -1
        )


def get_logging_config(settings: Settings) -> Dict:
    """
    Get the logging configuration.

    :param settings: The application settings.

    :return: The logging configuration.
    """
    log_level = settings.log_level
    formatter = logging.Formatter

    return {
        "version": 1,
        "disable_existing_loggers": True,
        "filters": {
            "correlation_id": {"()": CorrelationIdFilter, "uuid_length": 40},
            "endpoint_filter": {"()": EndpointFilter},
        },
        "formatters": {
            "stdout_formatter": {
                "()": formatter,
                "fmt": (
                    "%(asctime)s | %(name)s | [%(correlation_id)s] | %(process)d | %(module)s |"
                    " %(funcName)s | %(levelname)s | %(lineno)d | %(message)s"
                ),
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "filters": ["correlation_id", "endpoint_filter"],
                "formatter": "stdout_formatter",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "root": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "gunicorn.error": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
            "gunicorn": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }
