import argparse
import sys

from .app import JsonTreeApp


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        nargs='?',
        type=argparse.FileType(encoding='utf-8', mode='r'),
        metavar='PATH',
        help='path to file, or stdin',
        default=sys.stdin,
    )

    args = parser.parse_args()

    # See: https://github.com/Textualize/textual/issues/153#issuecomment-1256933121
    sys.stdin = open('/dev/tty')  # noqa

    app = JsonTreeApp(args.path)
    app.run()

    if not sys.stdin.closed:
        sys.stdin.close()


if __name__ == '__main__':
    _main()
