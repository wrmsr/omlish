from ..cli import CliModule


# @om-manifest
_CLI_MODULE = CliModule('dataclasses', __name__)


if __name__ == '__main__':
    from .cli import _main  # noqa

    _main()
