"""
TODO:
 - read from http
 - jmespath output flat, unquoted strs like jq '.[]'

==

jq Command options:
  -n, --null-input          use `null` as the single input value;
  -R, --raw-input           read each line as string instead of JSON;
  -s, --slurp               read all inputs into an array and use it as the single input value;
  -c, --compact-output      compact instead of pretty-printed output;
  -r, --raw-output          output strings without escapes and quotes;
      --raw-output0         implies -r and output NUL after each output;
  -j, --join-output         implies -r and output without newline after each output;
  -a, --ascii-output        output strings by only ASCII characters using escape sequences;
  -S, --sort-keys           sort keys of each object on output;
  -C, --color-output        colorize JSON output;
  -M, --monochrome-output   disable colored output;
      --tab                 use tabs for indentation;
      --indent n            use n spaces for indentation (max 7 spaces);
      --unbuffered          flush output stream after each output;
      --stream              parse the input value in streaming fashion;
      --stream-errors       implies --stream and report parse error as an array;
      --seq                 parse input/output as application/json-seq;
  -f, --from-file file      load filter from the file;
  -L directory              search modules from the directory;
      --arg name value      set $name to the string value;
      --argjson name value  set $name to the JSON value;
      --slurpfile name file set $name to an array of JSON values read from the file;
      --rawfile name file   set $name to string contents of file;
      --args                consume remaining arguments as positional string values;
      --jsonargs            consume remaining arguments as positional JSON values;
  -e, --exit-status         set exit status code based on the output;
  -V, --version             show the version;
  --build-configuration     show jq's build configuration;
  -h, --help                show the help;
  --                        terminates argument processing;
"""
import argparse
import codecs
import contextlib
import io
import json
import os
import subprocess
import sys
import typing as ta

from .... import check
from .... import lang
from .... import term
from ....lite.io import DelimitingBuffer
from ..render import JsonRenderer
from ..stream.build import JsonObjectBuilder
from ..stream.lex import JsonStreamLexer
from ..stream.parse import JsonStreamParser
from ..stream.render import StreamJsonRenderer
from .formats import FORMATS_BY_NAME
from .formats import Formats


if ta.TYPE_CHECKING:
    from ....specs import jmespath
else:
    jmespath = lang.proxy_import('....specs.jmespath', __package__)


##


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

    parser.add_argument('--stream', action='store_true')
    parser.add_argument('--stream-build', action='store_true')

    parser.add_argument('-l', '--lines', action='store_true')

    parser.add_argument('--read-buffer-size', type=int, default=0x4000)

    parser.add_argument('-f', '--format')

    parser.add_argument('-x', '--jmespath-expr')
    parser.add_argument('-F', '--flat', action='store_true')
    parser.add_argument('-R', '--raw', action='store_true')

    parser.add_argument('-z', '--compact', action='store_true')
    parser.add_argument('-p', '--pretty', action='store_true')
    parser.add_argument('-i', '--indent')
    parser.add_argument('-s', '--sort-keys', action='store_true')

    parser.add_argument('-c', '--color', action='store_true')

    parser.add_argument('-L', '--less', action='store_true')

    args = parser.parse_args()

    #

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

    kw: dict[str, ta.Any] = dict(
        indent=indent,
        separators=separators,
        sort_keys=args.sort_keys,
    )

    if args.jmespath_expr is not None:
        jp_expr = jmespath.compile(args.jmespath_expr)
    else:
        jp_expr = None

    def render_one(v: ta.Any) -> None:
        if args.raw:
            if not isinstance(v, str):
                raise TypeError(v)
            s = v

        elif args.color:
            s = JsonRenderer.render_str(
                v,
                **kw,
                style=term_color,
            )

        else:
            s = json.dumps(
                v,
                **kw,
            )

        print(s, file=out)

    def render_value(v: ta.Any) -> None:
        if jp_expr is not None:
            v = jp_expr.search(v)

        if args.flat:
            if isinstance(v, str):
                raise TypeError(v)

            for e in v:
                render_one(e)

        else:
            render_one(v)

    #

    fmt_name = args.format
    if fmt_name is None:
        if args.file is not None:
            ext = args.file.rpartition('.')[2]
            if ext in FORMATS_BY_NAME:
                fmt_name = ext
    if fmt_name is None:
        fmt_name = 'json'
    fmt = FORMATS_BY_NAME[fmt_name]

    if args.stream:
        check.arg(fmt is Formats.JSON.value)

    #

    with contextlib.ExitStack() as es:
        if args.file is None:
            in_file = sys.stdin.buffer

        else:
            in_file = es.enter_context(open(args.file, 'rb'))

        #

        if args.less:
            less = subprocess.Popen(
                [
                    'less',
                    *(['-R'] if args.color else []),
                ],
                stdin=subprocess.PIPE,
                encoding='utf-8',
            )
            out = check.not_none(less.stdin)

            def close_less():
                out.close()
                less.wait()

            es.enter_context(lang.defer(close_less))  # noqa

        else:
            out = sys.stdout

        #

        if args.stream:
            fd = in_file.fileno()
            decoder = codecs.getincrementaldecoder('utf-8')()

            with contextlib.ExitStack() as es2:
                lex = es2.enter_context(JsonStreamLexer())
                parse = es2.enter_context(JsonStreamParser())

                if args.stream_build:
                    build = es2.enter_context(JsonObjectBuilder())
                    renderer = None

                else:
                    renderer = StreamJsonRenderer(
                        style=term_color if args.color else None,
                        delimiter='\n',
                        **kw,
                    )
                    build = None

                while True:
                    buf = os.read(fd, args.read_buffer_size)

                    for s in decoder.decode(buf, not buf):
                        n = 0
                        for c in s:
                            for t in lex(c):
                                for e in parse(t):
                                    if renderer is not None:
                                        for r in renderer.render((e,)):
                                            out.write(r)

                                    if build is not None:
                                        for v in build(e):
                                            render_value(v)

                                    n += 1

                        if n:
                            out.flush()

                    if not buf:
                        break

                if renderer is not None:
                    out.write('\n')

        elif args.lines:
            fd = in_file.fileno()
            db = DelimitingBuffer()

            while buf := os.read(fd, args.read_buffer_size):
                for chunk in db.feed(buf):
                    s = check.isinstance(chunk, bytes).decode('utf-8')
                    v = fmt.load(io.StringIO(s))
                    render_value(v)

        else:
            with io.TextIOWrapper(in_file) as tw:
                v = fmt.load(tw)
            render_value(v)


if __name__ == '__main__':
    _main()
