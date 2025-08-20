# @omlish-manifest
_CLI_MODULE = {'!omdev.cli.types.CliModule': {
    'name': 'pidfiles',
    'module': __name__,
}}


if __name__ == '__main__':
    from .cli import _main  # noqa

    _main()
