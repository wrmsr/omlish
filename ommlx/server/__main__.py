# @omlish-manifest omdev.cli.CliModule(['minichain-server', 'mcs'], __name__)


if __name__ == '__main__':
    from .cli import _main  # noqa

    _main()
