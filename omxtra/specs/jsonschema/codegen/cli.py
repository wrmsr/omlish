import os.path
import sys
import typing as ta

from omlish.argparse import all as ap
from omlish.formats.json import all as json
from omlish.logs.std.standard import configure_standard_logging
from omlish.specs import jsonschema as js

from .generator import JsonSchemaCodeGen


##


def _load_schema(path: str) -> ta.Any:
    if path == '-':
        return json.loads(sys.stdin.read())

    with open(path) as f:
        return json.load(f)


def _parse_schema(obj: ta.Any) -> js.Keywords:
    return js.KeywordParser(
        allow_unknown='x-only',
        allow_specific_unknowns={'discriminator'},
    ).parse_keywords(obj)


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('schema'),
        ap.arg('-o', '--output'),
    )
    def gen(self) -> None:
        src = JsonSchemaCodeGen(_parse_schema(_load_schema(self.args.schema))).gen_module()

        if self.args.output is not None:
            os.makedirs(os.path.dirname(os.path.abspath(self.args.output)), exist_ok=True)
            with open(self.args.output, 'w') as f:
                f.write(src)
        else:
            print(src, end='')

    @ap.cmd(
        ap.arg('schema'),
    )
    def check(self) -> None:
        JsonSchemaCodeGen(_parse_schema(_load_schema(self.args.schema))).build_module()


def _main() -> None:
    configure_standard_logging()

    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
