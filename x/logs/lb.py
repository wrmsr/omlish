import sys

import logbook


def _main():
    logbook.StreamHandler(sys.stdout).push_application()
    logbook.warn('This is a warning')


if __name__ == '__main__':
    _main()
