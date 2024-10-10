import argparse
import contextlib
import json
import sys
import typing as ta

from omlish import term


class JsonPrinter:
    def __init__(
            self,
            out: ta.TextIO | None = None,
            indent: int | str | None = None,
            separators: tuple[str, str] | None = None,
    ) -> None:
        super().__init__()

        self._out = out if out is not None else sys.stdout
        if isinstance(indent, (str, int)):
            self._indent = (' ' * indent) if isinstance(indent, int) else indent
            self._endl = '\n'
            if separators is None:
                separators = (', ', ': ')
        elif indent is None:
            self._indent = self._endl = ''
            if separators is None:
                separators = (',', ':')
        else:
            raise TypeError(indent)
        self._comma, self._colon = separators

        self._level = 0
        self._literals = {
            True: 'true',
            False: 'false',
            None: 'null',
        }

    def _write(self, s: str) -> None:
        if s:
            self._out.write(s)

    def _write_indent(self) -> None:
        if self._indent:
            self._write(self._endl)
            if self._level:
                self._write(self._indent * self._level)

    def _print(self, o: ta.Any) -> None:
        if o is None or isinstance(o, bool):
            self._write(self._literals[o])

        elif isinstance(o, (str, int, float)):
            self._write(json.dumps(o))

        elif isinstance(o, ta.Mapping):
            self._write('{')
            self._level += 1
            for i, (k, v) in enumerate(o.items()):
                if i:
                    self._write(self._comma)
                self._write_indent()
                self._print(k)
                self._write(self._colon)
                self._print(v)
            self._level -= 1
            if o:
                self._write_indent()
            self._write('}')

        elif isinstance(o, ta.Sequence):
            self._write('[')
            self._level += 1
            for i, e in enumerate(o):
                if i:
                    self._write(self._comma)
                self._write_indent()
                self._print(e)
            self._level -= 1
            if o:
                self._write_indent()
            self._write(']')

        else:
            raise TypeError(o)

    def print(self, o: ta.Any) -> None:
        self._print(o)
        self._write(self._endl)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('-c', '--color', action='store_true')
    args = parser.parse_args()

    with contextlib.ExitStack() as es:
        if args.file is None:
            in_file = sys.stdin
        else:
            in_file = es.enter_context(open(args.file))

        data = json.load(in_file)

    if args.color:
        JsonPrinter(sys.stdout, indent=2).print(data)

    else:
        pretty_json = json.dumps(data, indent=4)
        print(pretty_json)


if __name__ == "__main__":
    main()