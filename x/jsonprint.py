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
            separators: tuple[str, str] = (', ', ': '),
    ) -> None:
        super().__init__()

        self._out = out if out is not None else sys.stdout
        if isinstance(indent, (str, int)):
            self._indent = (' ' * indent) if isinstance(indent, int) else indent
            self._endl = '\n'
        else:
            self._indent = self._endl = ''
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

    def print(self, o: ta.Any) -> None:
        if o is None or isinstance(o, bool):
            self._write(self._literals[o])

        elif isinstance(o, (str, int, float)):
            self._write(json.dumps(o))

        elif isinstance(o, ta.Mapping):
            self._write('{')
            for i, (k, v) in enumerate(o.items()):
                if i:
                    self._write(self._comma)
                self.print(k)
                self._write(self._colon)
                self.print(v)
            self._write('}')

        elif isinstance(o, ta.Sequence):
            self._write('[')
            for i, e in enumerate(o):
                if i:
                    self._write(self._comma)
                self.print(e)
            self._write(']')

        else:
            raise TypeError(o)


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
        JsonPrinter(sys.stdout).print(data)

    else:
        pretty_json = json.dumps(data, indent=4)
        print(pretty_json)


if __name__ == "__main__":
    main()