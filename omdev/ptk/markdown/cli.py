import argparse
import sys

from ... import ptk
from .markdown import Markdown
from .styles import MARKDOWN_STYLE


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

    ptk.print_formatted_text(
        Markdown(src),
        style=ptk.Style(list(MARKDOWN_STYLE)),
    )


if __name__ == '__main__':
    _main()
