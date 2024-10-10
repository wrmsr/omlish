import argparse
import contextlib
import json
import subprocess
import sys
import typing as ta

from ... import term
from .render import JsonRenderer


def term_color(o: ta.Any, state: JsonRenderer.State) -> tuple[str, str]:
    if state is JsonRenderer.State.KEY:
        return term.SGR(term.SGRs.FG.BRIGHT_BLUE), term.SGR(term.SGRs.RESET)
    elif isinstance(o, str):
        return term.SGR(term.SGRs.FG.GREEN), term.SGR(term.SGRs.RESET)
    else:
        return '', ''


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('file', nargs='?')
    parser.add_argument('-z', '--compact', action='store_true')
    parser.add_argument('-p', '--pretty', action='store_true')
    parser.add_argument('-i', '--indent')
    parser.add_argument('-s', '--sort-keys', action='store_true')
    parser.add_argument('-c', '--color', action='store_true')
    parser.add_argument('-l', '--less', action='store_true')
    args = parser.parse_args()

    separators = None
    if args.compact:
        separators = (',', ':')

    indent = None
    if args.pretty:
        indent = 2
    if args.indent:
        try:
            indent = int(args.indent)
        except ValueError:
            indent = args.indent

    with contextlib.ExitStack() as es:
        if args.file is None:
            in_file = sys.stdin
        else:
            in_file = es.enter_context(open(args.file))

        data = json.load(in_file)

    kw: dict[str, ta.Any] = dict(
        indent=indent,
        separators=separators,
        sort_keys=args.sort_keys,
    )

    if args.color:
        out = JsonRenderer.render_str(
            data,
            **kw,
            style=term_color,
        )

    else:
        out = json.dumps(
            data,
            **kw,
        )

    if args.less:
        subprocess.run(
            [
                'less',
                *(['-R'] if args.color else []),
            ],
            input=out.encode(),
            check=True,
        )

    else:
        print(out)


if __name__ == '__main__':
    _main()
