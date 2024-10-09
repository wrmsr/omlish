# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': ['jmespath', 'jp'],
    'mod_name': __name__,
}}


if __name__ == '__main__':
    from .cli import _main

    _main()
