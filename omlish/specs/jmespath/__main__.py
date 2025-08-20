# @omlish-manifest
_CLI_MODULE = {'!omdev.cli.types.CliModule': {
    'name': ['jmespath', 'jp'],
    'module': __name__,
}}


if __name__ == '__main__':
    from .cli import _main

    _main()
