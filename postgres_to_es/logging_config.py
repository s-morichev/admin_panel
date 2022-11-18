import logging.config
from settings import APP_CONFIG

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s: %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
    if APP_CONFIG.debug:
        logging.getLogger("root").setLevel(logging.DEBUG)
    logging.getLogger("backoff").addHandler(logging.StreamHandler())
