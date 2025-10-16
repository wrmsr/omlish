from omlish.argparse import all as argparse

from .app import IrcApp


##


def _main() -> None:
    parser = argparse.ArgumentParser(description='Simple IRC client using Textual')
    parser.add_argument(
        '-x',
        action='append',
        dest='commands',
        help='Execute slash command on startup (can be specified multiple times)',
    )
    args = parser.parse_args()

    app = IrcApp(
        startup_commands=args.commands,
    )
    app.run()


if __name__ == '__main__':
    _main()
