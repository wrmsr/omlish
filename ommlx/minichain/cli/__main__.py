from omdev.cli import CliModule


# @omlish-manifest
_CLI_MODULE = CliModule('mc', __name__)


if __name__ == '__main__':
    from .main import _main

    _main()
