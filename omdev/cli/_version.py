from .. import __about__
from .types import CliModule


# @omlish-manifest
_CLI_MODULE = CliModule('version', __name__)


def _main() -> None:
    print(__about__.__version__)


if __name__ == '__main__':
    _main()
