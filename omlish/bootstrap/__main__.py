# @omlish-manifest
_CLI_MODULE = {'!omdev.cli.types.CliModule': {
    'name': 'bootstrap',
    'module': __name__,
}}


if __name__ == '__main__':
    from .main import _main

    _main()
