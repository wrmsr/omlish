import logging
import typing as ta

from ..auto import log


def configure_standard_logging(level: ta.Any = None) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(name)s %(levelname)s %(module)s %(message)s'))
    logging.root.addHandler(handler)
    if level is not None:
        logging.root.setLevel(level)
    return handler


def test_runtime():
    log.info('hi')
    log.wrapped.info('hi2')


def _main():
    configure_standard_logging('INFO')
    test_runtime()


if __name__ == '__main__':
    _main()
