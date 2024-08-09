#!/usr/bin/env python3
"""
Hi!
"""
# also
import os.path  # noqa
import pprint
import typing as ta  # noqa

from omlish.os import PAGE_SIZE

from ...std.cached import cached_nullary
from ...std.check import check_not_none
from ...std.logging import log
from ...std.logging import setup_standard_logging
from ...std.runtime import check_runtime_version
from ...std.subprocesses import subprocess_check_output


@cached_nullary
def _foo():
    return 5


def _main() -> None:
    """Docstring"""

    check_runtime_version()
    setup_standard_logging()
    log.info('hi')

    # Comment
    check_not_none(_foo())  # Inline comment

    pprint.pprint('hi')

    print(subprocess_check_output('uptime'))

    print(PAGE_SIZE)


if __name__ == '__main__':
    _main()
