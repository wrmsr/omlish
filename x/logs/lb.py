import sys

import logbook

from omlish import logs  # noqa


def _main():
    # logs.configure_standard_logging()
    logbook.StreamHandler(sys.stdout).push_application()
    logbook.warn('This is a warning')


if __name__ == '__main__':
    _main()
