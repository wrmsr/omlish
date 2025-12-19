import logging


##


NOISY_LOGGER_LEVELS: dict[str, int] = {
    'boto3.resources.action': logging.WARNING,
    'datadog.dogstatsd': logging.WARNING,
    'elasticsearch': logging.WARNING,
    'httpcore': logging.INFO,
    'httpx': logging.WARNING,
    'kazoo.client': logging.WARNING,
    'markdown_it': logging.INFO,
    'requests.packages.urllib3.connectionpool': logging.WARNING,
}


def silence_noisy_loggers() -> None:
    for name, level in NOISY_LOGGER_LEVELS.items():
        logging.getLogger(name).setLevel(level)
