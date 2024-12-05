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

from omlish import check
from omlish import lang
from omlish.funcs import pipes as fp

from .formats import FORMATS_BY_NAME
from .formats import Format
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


T = ta.TypeVar('T')
U = ta.TypeVar('U')


def _build_args_parser() -> argparse.ArgumentParser:
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

    return parser


def _parse_args(args: ta.Any = None) -> ta.Any:
    return _build_args_parser().parse_args(args)


@dc.dataclass(frozen=True, kw_only=True)
class RunConfiguration:
    format: Format
    processing: ProcessingOptions
    rendering: RenderingOptions


def _process_args(args: ta.Any) -> RunConfiguration:
    fmt_name = args.format
    if fmt_name is None:
        if args.file is not None:
            ext = args.file.rpartition('.')[2]
            if ext in FORMATS_BY_NAME:
                fmt_name = ext
    if fmt_name is None:
        fmt_name = 'json'
    format = FORMATS_BY_NAME[fmt_name]  # noqa

    if args.stream:
        check.arg(format is Formats.JSON.value)

    #

    processing = ProcessingOptions(
        jmespath_expr=args.jmespath_expr,
        flat=args.flat,
    )

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

    rendering = RenderingOptions(
        indent=indent,
        separators=separators,
        sort_keys=args.sort_keys,
        raw=args.raw,
        unicode=args.unicode,
        color=args.color,
    )

    #

    return RunConfiguration(
        format=format,
        processing=processing,
        rendering=rendering,
    )


def _main() -> None:
    args = _parse_args()

    #

    cfg = _process_args(args)

    #

    with contextlib.ExitStack() as es:
        if args.file is None:
            in_file = sys.stdin.buffer

        else:
            in_file = es.enter_context(open(args.file, 'rb'))

        def yield_input() -> ta.Generator[bytes, None, None]:
            fd = check.isinstance(in_file.fileno(), int)

            while True:
                buf = os.read(fd, args.read_buffer_size)

                yield buf

                if not buf:
                    break

        #

        if args.less:
            less = subprocess.Popen(
                [
                    'less',
                    *(['-R'] if cfg.rendering.color else []),
                ],
                stdin=subprocess.PIPE,
                encoding='utf-8',
            )
            out = check.not_none(less.stdin)

            def close_less() -> None:
                out.close()
                less.wait()

            es.enter_context(lang.defer(close_less))  # noqa

        else:
            out = sys.stdout

        #

        parser: ta.Any
        renderer: ta.Any

        if args.stream:
            with contextlib.ExitStack() as es2:
                parser = es2.enter_context(StreamParser())

                def flush_output(
                        fn: ta.Callable[[T], ta.Iterable[U]],
                        i: T,
                ) -> ta.Generator[U, None, None]:
                    n = 0
                    for o in fn(i):
                        yield o
                        n += 1
                    if n:
                        out.flush()

                pipeline: ta.Any

                if args.stream_build:
                    builder: StreamBuilder = es2.enter_context(StreamBuilder())
                    processor = Processor(cfg.processing)
                    renderer = EagerRenderer(cfg.rendering)
                    trailing_newline = False

                    def append_newlines(
                            fn: ta.Callable[[T], ta.Iterable[str]],
                            i: T,
                    ) -> ta.Generator[str, None, None]:
                        yield from fn(i)
                        yield '\n'

                    pipeline = lambda v: (renderer.render(v),)  # Any -> [str]  # noqa
                    pipeline = fp.bind(append_newlines, pipeline)  # Any -> [str]
                    pipeline = fp.bind(lang.flatmap, pipeline)  # [Any] -> [str]
                    pipeline = fp.pipe(fp.bind(lang.flatmap, processor.process), pipeline)  # [Any] -> [str]
                    pipeline = fp.pipe(fp.bind(lang.flatmap, builder.build), pipeline)  # [JsonStreamParserEvent] -> [str]  # noqa
                    pipeline = fp.pipe(parser.parse, pipeline)  # bytes -> [str]

                else:
                    renderer = StreamRenderer(cfg.rendering)
                    trailing_newline = True

                    pipeline = renderer.render  # JsonStreamParserEvent -> [str]
                    pipeline = fp.bind(lang.flatmap, pipeline)  # [JsonStreamParserEvent] -> [str]
                    pipeline = fp.pipe(parser.parse, pipeline)  # bytes -> [str]

                pipeline = fp.bind(flush_output, pipeline)  # bytes -> [str]

                for buf in yield_input():
                    for s in pipeline(buf):
                        print(s, file=out, end='')

                if trailing_newline:
                    print(file=out)

        elif args.lines:
            parser = DelimitingParser(cfg.format)
            processor = Processor(cfg.processing)
            renderer = EagerRenderer(cfg.rendering)

            for buf in yield_input():
                for v in parser.parse(buf):
                    for e in processor.process(v):
                        s = renderer.render(e)
                        print(s, file=out)

        else:
            parser = EagerParser(cfg.format)
            processor = Processor(cfg.processing)
            renderer = EagerRenderer(cfg.rendering)

            with io.TextIOWrapper(in_file) as tf:
                v = parser.parse(tf)

            for e in processor.process(v):
                s = renderer.render(e)
                print(s, file=out)


if __name__ == '__main__':
    _main()
