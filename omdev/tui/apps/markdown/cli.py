import argparse
import sys

from ... import rich


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    args = parser.parse_args()

    if args.file is not None:
        with open(args.file) as f:
            src = f.read()
    else:
        src = sys.stdin.read()

    console = rich.Console()
    markdown = rich.Markdown(src)
    console.print(markdown)
    print()


if __name__ == '__main__':
    _main()
