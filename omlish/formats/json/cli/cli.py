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
import contextlib
import dataclasses as dc
import io
import os
import subprocess
import sys
import typing as ta

from .... import check
from .... import lang
from .formats import FORMATS_BY_NAME
from .formats import Formats
from .parsing import DelimitingParser
from .parsing import EagerParser
from .parsing import StreamBuilder
from .parsing import StreamParser
from .processing import ProcessingOptions
from .processing import Processor
from .rendering import EagerRenderer
from .rendering import RenderingOptions
from .rendering import StreamRenderer


"""
        fd = in_file.fileno()
        decoder = codecs.getincrementaldecoder('utf-8')()

        with contextlib.ExitStack() as es2:
            lex = es2.enter_context(JsonStreamLexer())
            parse = es2.enter_context(JsonStreamParser())

            while True:
                buf = os.read(fd, args.read_buffer_size)

                for s in decoder.decode(buf, not buf):
                    n = 0
                    for c in s:
                        for t in lex(c):
                            for e in parse(t):
                                yield e
                                n += 1

                    if n:
                        out.flush()

                if not buf:
                    break

            if renderer is not None:
                out.write('\n')

"""


class Cli(lang.ExitStacked):
    @dc.dataclass(frozen=True)
    class Options:
        pass

    def __init__(
            self,
    ) -> None:
        super().__init__()

    #




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

    parser.add_argument('-z', '--compact', action='store_true')
    parser.add_argument('-p', '--pretty', action='store_true')
    parser.add_argument('-i', '--indent')
    parser.add_argument('-s', '--sort-keys', action='store_true')
    parser.add_argument('-R', '--raw', action='store_true')
    parser.add_argument('-U', '--unicode', action='store_true')
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

    r_opts = RenderingOptions(
        indent=indent,
        separators=separators,
        sort_keys=args.sort_keys,
        raw=args.raw,
        unicode=args.unicode,
        color=args.color,
    )

    #

    p_opts = ProcessingOptions(
        jmespath_expr=args.jmespath_expr,
        flat=args.flat,
    )

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

            with contextlib.ExitStack() as es2:
                parser: StreamParser = es2.enter_context(StreamParser())

                if args.stream_build:
                    builder: StreamBuilder = es2.enter_context(StreamBuilder())
                    processor = Processor(p_opts)
                    renderer = EagerRenderer(r_opts)

                    while True:
                        buf = os.read(fd, args.read_buffer_size)

                        n = 0
                        for e in parser.parse(buf):
                            for v in builder.build(e):
                                for o in processor.process(v):
                                    for s in renderer.render(o):
                                        print(s, file=out, end='')
                                        n += 1
                        if n:
                            out.flush()

                        if not buf:
                            break

                else:
                    renderer = StreamRenderer(r_opts)

                    while True:
                        buf = os.read(fd, args.read_buffer_size)

                        n = 0
                        for e in parser.parse(buf):
                            for s in renderer.render(e):
                                print(s, file=out, end='')
                                n += 1
                        if n:
                            out.flush()

                        if not buf:
                            break

                    print(file=out)

        elif args.lines:
            fd = in_file.fileno()

            parser = DelimitingParser(fmt)
            processor = Processor(p_opts)
            renderer = EagerRenderer(r_opts)

            while b := os.read(fd, args.read_buffer_size):
                for v in parser.parse(b):
                    for e in processor.process(v):
                        s = renderer.render(e)
                        print(s, file=out)

        else:
            parser = EagerParser(fmt)
            processor = Processor(p_opts)
            renderer = EagerRenderer(r_opts)

            with io.TextIOWrapper(in_file) as tf:
                v = parser.parse(tf)

            for e in processor.process(v):
                s = renderer.render(e)
                print(s, file=out)


if __name__ == '__main__':
    _main()
