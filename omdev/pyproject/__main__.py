from ..cli import CliModule


# @omlish-manifest
_CLI_MODULE = CliModule('pyproject', __name__)


if __name__ == '__main__':
    from .cli import _main

    _main()
