import structlog


def inject_context_dict(_, __, event_dict):
    """Add the structlog context dict to log events generated by the stdlib logging library.

    >>> import structlog
    >>> from django_structlog.processors import inject_context_dict
    >>>
    >>> LOGGING = {
    ...     "version": 1,
    ...     "disable_existing_loggers": False,
    ...     "formatters": {
    ...         "json_formatter": {
    ...             "()": structlog.stdlib.ProcessorFormatter,
    ...             "processor": structlog.processors.JSONRenderer(),
    ...             # ADD THIS SECTION
    ...             "foreign_pre_chain": [
    ...                 inject_context_dict,
    ...                 structlog.processors.TimeStamper(fmt="iso"),
    ...                 structlog.stdlib.add_logger_name,
    ...                 structlog.stdlib.add_log_level,
    ...                 structlog.stdlib.PositionalArgumentsFormatter(),
    ...             ],
    ...         },
    ...     },
    ...     "handlers": {
    ...         "json_file": {
    ...             "class": "logging.handlers.WatchedFileHandler",
    ...             "filename": "logs/json.log",
    ...             "formatter": "json_formatter",
    ...         }
    ...     },
    ...     "loggers": {
    ...         "django_structlog": {
    ...             "handlers": ["json_file"],
    ...             "level": "INFO",
    ...         },
    ...         # ADD THE STANDARD LOGGERS NAMES
    ...         "foreign_logger": {
    ...             "handlers": ["json_file"],
    ...             "level": "INFO",
    ...         },
    ...     },
    ... }
    >>>

    Logging with a standard logger:

    >>> import logging
    >>> logging.getLogger("foreign_logger").info("This is a standard logger")

    Results::

        {
            "event": "This is a standard logger",
            "request_id": "da006c53-abdc-4b26-961d-e45f85152029",
            "user_id": null,
            "ip": "0.0.0.0",
            "timestamp": "2020-11-27T03:06:37.335676Z",
            "logger": "foreign_logger",
            "level": "info"
        }

    """
    context_class = structlog.get_config().get("context_class")

    if context_class:
        for key, value in context_class().items():
            if key not in event_dict:
                event_dict[key] = value

    return event_dict