import logging


NOISY_LOGGERS: set[str] = {
    'boto3.resources.action',
    'datadog.dogstatsd',
    'elasticsearch',
    'kazoo.client',
    'requests.packages.urllib3.connectionpool',
}


def silence_noisy_loggers() -> None:
    for noisy_logger in NOISY_LOGGERS:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
