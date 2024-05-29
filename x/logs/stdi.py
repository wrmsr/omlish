import logging  # noqa
import types  # noqa
import typing as ta  # noqa

from omlish import logs


def _main():
    logs.configure_standard_logging(logging.INFO)
    try:
        raise ValueError('barf')
    except Exception:
        logging.info('hi', stack_info=True, exc_info=True)


if __name__ == '__main__':
    _main()
