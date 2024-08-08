import os.path  # noqa
import pprint
import typing as ta  # noqa

from .std.cached import cached_nullary
from .std.check import check_not_none


@cached_nullary
def _foo():
    return 5


def _main() -> None:
    """Docstring"""

    # Comment
    check_not_none(_foo())  # Inline comment

    pprint.pprint('hi')


if __name__ == '__main__':
    _main()
