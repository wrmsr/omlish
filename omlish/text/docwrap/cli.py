"""
Usable as a jetbrains external tool:
  `om docwrap -i "$FilePath$" -s "$SelectionStartLine$" -e "$SelectionEndLine$"`

TODO:
 - -> omdev.tools
 - at least file extension awareness, preserve say # prefixes in py comment blocks
  - maybe treesitter? or just special case py
"""
import argparse
import sys
import typing as ta

from .api import docwrap
from .rendering import render


##


def _main(argv: ta.Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')

    parser.add_argument('-w', '--width', type=int, default=120)

    parser.add_argument('-s', '--start-line', type=int)
    parser.add_argument('-e', '--end-line', type=int)
    parser.add_argument('-i', '--in-place', action='store_true')

    args = parser.parse_args(argv)

    #

    if args.file:
        with open(args.file) as f:
            in_txt = f.read()
    else:
        if args.in_place:
            raise ValueError('Cannot use --in-place without specifying a file')
        in_txt = sys.stdin.read()

    in_lines = in_txt.splitlines()

    #

    if args.start_line is not None and args.end_line is not None:
        if args.start_line > args.end_line:
            raise ValueError('Start line cannot be greater than end line')
    if args.start_line is not None:
        if args.start_line < 1:
            raise ValueError('Start line cannot be less than 1')
        start_line = args.start_line - 1
    else:
        start_line = 0
    if args.end_line is not None:
        if args.end_line < 1:
            raise ValueError('End line cannot be less than 1')
        end_line = args.end_line - 1
    else:
        end_line = len(in_lines) - 1

    #

    in_part = '\n'.join(in_lines[start_line:end_line + 1])

    root = docwrap(
        in_part,
        width=args.width,
    )

    out_part = render(root)

    out_txt = '\n'.join([
        *in_lines[:start_line],
        out_part,
        *in_lines[end_line + 1:],
        '',
    ])

    #

    if args.in_place:
        with open(args.file, 'w') as f:
            f.write(out_txt)
    else:
        print(out_txt)


if __name__ == '__main__':
    _main()
