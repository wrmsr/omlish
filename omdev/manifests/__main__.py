from ..cli import CliModule


# @omlish-manifest
_CLI_MODULE = CliModule('manifests', __name__)


if __name__ == '__main__':
    from .main import _main  # noqa

    _main()
