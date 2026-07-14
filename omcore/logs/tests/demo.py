import logging

from ..std.loggers import StdLogger
from ..std.standard import configure_standard_logging


##


def _main() -> None:
    configure_standard_logging()

    log = StdLogger(logging.getLogger(__name__))
    log.info('hi')


if __name__ == '__main__':
    _main()
