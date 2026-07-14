from ..cli import CliModule


# @om-manifest
_CLI_MODULE = CliModule('amalg', __name__)


if __name__ == '__main__':
    from .cli.main import _main  # noqa

    _main()
