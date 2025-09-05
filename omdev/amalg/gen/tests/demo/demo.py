"""
Hi!
"""
# also
import os.path  # noqa
import pprint
import typing as ta  # noqa

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.logs.modules import get_module_logger
from omlish.lite.runtime import check_lite_runtime_version
from omlish.logs.standard import configure_standard_logging
from omlish.os.sizes import PAGE_SIZE
from omlish.os.temp import make_temp_file  # noqa
from omlish.subprocesses.sync import subprocesses

from .incl.foo import foo


log = get_module_logger(globals())  # noqa


##


@cached_nullary
def _foo():
    return 5


def _main() -> None:
    """Docstring"""

    check_lite_runtime_version()
    configure_standard_logging()
    log.info('hi')

    # Comment
    check.not_none(_foo())  # Inline comment

    pprint.pprint(foo())

    print(subprocesses.check_output('uptime'))

    print(PAGE_SIZE)


if __name__ == '__main__':
    _main()
