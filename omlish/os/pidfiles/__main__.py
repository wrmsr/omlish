# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'pidfiles',
    'mod_name': __name__,
}}


if __name__ == '__main__':
    from .cli import _main  # noqa

    _main()
