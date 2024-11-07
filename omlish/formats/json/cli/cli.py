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
import dataclasses as dc
import io
import json
import os
import subprocess
import sys
import typing as ta

from .... import cached
from .... import check
from .... import lang
from .... import term
from ....lite.io import DelimitingBuffer
from ..render import JsonRenderer
from ..stream.build import JsonObjectBuilder
from ..stream.lex import JsonStreamLexer
from ..stream.parse import JsonStreamParser
from ..stream.parse import JsonStreamParserEvent
from ..stream.render import StreamJsonRenderer
from .formats import FORMATS_BY_NAME
from .processing import ProcessingOptions
from .formats import Format
from .formats import Formats
from .rendering import RenderingOptions


##


##




class StreamBuilder(lang.ExitStacked):
    _builder: JsonObjectBuilder | None = None

    def __enter__(self) -> ta.Self:
        super().__enter__()
        self._builder = self._enter_context(JsonObjectBuilder())
        return self

    def build(self, e: JsonStreamParserEvent) -> ta.Generator[ta.Any, None, None]:
        yield from check.not_none(self._builder)(e)

##


class StreamParser(lang.ExitStacked):
    _decoder: codecs.IncrementalDecoder
    _lex: JsonStreamLexer
    _parse: JsonStreamParser

    def __enter__(self) -> ta.Self:
        super().__enter__()
        self._decoder = codecs.getincrementaldecoder('utf-8')()
        self._lex = self._enter_context(JsonStreamLexer())
        self._parse = self._enter_context(JsonStreamParser())
        return self

    def parse(self, b: bytes) -> ta.Generator[JsonStreamParserEvent, None, None]:
        for s in self._decoder.decode(b, not b):
            for c in s:
                for t in self._lex(c):
                    for e in self._parse(t):
                        yield e


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


class LinesParser:
    def __init__(
            self,
            fmt: Format,
    ) -> None:
        super().__init__()

        self._fmt = fmt

        self._db = DelimitingBuffer()

    def parse(self, b: bytes) -> ta.Generator[ta.Any, None, None]:
        for chunk in self._db.feed(b):
            s = check.isinstance(chunk, bytes).decode('utf-8')
            v = self._fmt.load(io.StringIO(s))
            yield v


class SimpleParser:
    def run_simple(self) -> None:
        with io.TextIOWrapper(in_file) as tw:
            v = fmt.load(tw)
        render_value(v)


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

        elif args.lines:

        else:


if __name__ == '__main__':
    _main()
