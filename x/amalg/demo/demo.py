import os.path  # noqa
import pprint
import typing as ta  # noqa

from .stdlib import check_not_none


def _main() -> None:
    check_not_none(5)

    pprint.pprint('hi')


if __name__ == '__main__':
    _main()
