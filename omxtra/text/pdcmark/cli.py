import argparse
import sys

from .parsing import parse
from .rendering.html import render_html


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()

    if args.file == '-':
        src = sys.stdin.read()
    else:
        with open(args.file) as f:
            src = f.read()

    events = parse(src)
    html = render_html(events)

    print(html)


if __name__ == '__main__':
    _main()
