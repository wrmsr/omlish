import argparse
import contextlib
import dataclasses as dc
import enum
import json
import subprocess
import sys
import typing as ta

from ... import lang
from ... import term
from .render import JsonRenderer


if ta.TYPE_CHECKING:
    import tomllib

    import yaml

    from .. import dotenv
    from .. import props

else:
    tomllib = lang.proxy_import('tomllib')

    yaml = lang.proxy_import('yaml')

    dotenv = lang.proxy_import('..dotenv', __package__)
    props = lang.proxy_import('..props', __package__)


def term_color(o: ta.Any, state: JsonRenderer.State) -> tuple[str, str]:
    if state is JsonRenderer.State.KEY:
        return term.SGR(term.SGRs.FG.BRIGHT_BLUE), term.SGR(term.SGRs.RESET)
    elif isinstance(o, str):
        return term.SGR(term.SGRs.FG.GREEN), term.SGR(term.SGRs.RESET)
    else:
        return '', ''


@dc.dataclass(frozen=True)
class Format:
    names: ta.Sequence[str]
    load: ta.Callable[[ta.TextIO], ta.Any]


class Formats(enum.Enum):
    JSON = Format(['json'], json.load)
    YAML = Format(['yaml', 'yml'], lambda f: yaml.safe_load(f))
    TOML = Format(['toml'], lambda f: tomllib.loads(f.read()))
    ENV = Format(['env', 'dotenv'], lambda f: dotenv.dotenv_values(stream=f))
    PROPS = Format(['properties', 'props'], lambda f: dict(props.Properties().load(f.read())))


FORMATS_BY_NAME: ta.Mapping[str, Format] = {
    n: f
    for e in Formats
    for f in [e.value]
    for n in f.names
}


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('file', nargs='?')
    parser.add_argument('-f', '--format')
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

    fmt_name = args.format
    if fmt_name is None:
        if args.file is not None:
            ext = args.file.rpartition('.')[2]
            if ext in FORMATS_BY_NAME:
                fmt_name = ext
    if fmt_name is None:
        fmt_name = 'json'
    fmt = FORMATS_BY_NAME[fmt_name]

    with contextlib.ExitStack() as es:
        if args.file is None:
            in_file = sys.stdin
        else:
            in_file = es.enter_context(open(args.file))

        data = fmt.load(in_file)

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
