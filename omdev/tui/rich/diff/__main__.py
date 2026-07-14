from ....cli import CliModule


# @om-manifest
_CLI_MODULE = CliModule('tui/diff', __name__)


if __name__ == '__main__':
    from .cli import _main

    _main()
