# Copyright (c) 2025 Darren Burns
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import os
import pathlib
import sys

from rich.console import Console

from omlish import lang

from ....diffs.parsing import parse_patch
from .rendering import THEME
from .rendering import render_diff


##


@lang.cached_function
def console() -> Console:
    force_width, _ = os.get_terminal_size(2)

    return Console(
        force_terminal=True,
        width=force_width,
        theme=THEME,
    )


##


def find_git_root() -> pathlib.Path:
    cwd = pathlib.Path.cwd()
    if (cwd / '.git').exists():
        return pathlib.Path.cwd()

    for directory in cwd.parents:
        if (directory / '.git').exists():
            return directory

    return cwd


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('-r', '--root')
    args = parser.parse_args()

    try:
        if args.root:
            project_root = pathlib.Path(args.root)
        else:
            project_root = find_git_root()

        if args.file is not None:
            with open(args.file) as f:
                diff = f.read()

        else:
            input = sys.stdin.readlines()  # noqa
            diff = ''.join(input)

        patch_set = parse_patch(diff)

        render_diff(
            console(),
            patch_set,
            project_root,
        )

    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output to devnull to avoid another BrokenPipeError
        # at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)

    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    _main()
