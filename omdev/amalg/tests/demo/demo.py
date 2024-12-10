#!/usr/bin/env python3
"""
Hi!
"""
# also
import os.path  # noqa
import pprint
import typing as ta  # noqa

from omlish.os import PAGE_SIZE
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.logs import log
from omlish.lite.logs import configure_standard_logging
from omlish.lite.runtime import check_runtime_version
from omlish.lite.subprocesses import subprocess_check_output

from .incl.foo import foo


@cached_nullary
def _foo():
    return 5


def _main() -> None:
    """Docstring"""

    check_runtime_version()
    configure_standard_logging()
    log.info('hi')

    # Comment
    check.not_none(_foo())  # Inline comment

    pprint.pprint(foo())

    print(subprocess_check_output('uptime'))

    print(PAGE_SIZE)


if __name__ == '__main__':
    _main()
