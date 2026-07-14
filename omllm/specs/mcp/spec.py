"""
https://github.com/modelcontextprotocol/modelcontextprotocol/blob/9b15ff98b87d6a6a54055f4189feb22e750d9389/schema/2025-03-26/schema.json
"""
import os.path
import typing as ta

from omdev.cache import data as dcache
from omcore import lang
from omcore.argparse import all as ap
from omcore.formats.json import all as json
from omcore.specs import jsonschema as js


##


MCP_SPEC_VERSION = '2025-06-18'

MCP_SPEC_DATA = dcache.GitSpec(
    'https://github.com/modelcontextprotocol/modelcontextprotocol',
    rev='ef175d72115b25f0a0e89dd52f40442761b6a380',
    subtrees=[
        MCP_SPEC_PATH := f'schema/{MCP_SPEC_VERSION}/schema.json',
    ],
)


@lang.cached_function(lock=True)
def spec_path() -> str:
    spec_dir = dcache.default().get(MCP_SPEC_DATA)
    return os.path.join(spec_dir, MCP_SPEC_PATH)


@lang.cached_function(lock=True)
def spec_src() -> str:
    with open(spec_path()) as f:
        return f.read()


@lang.cached_function(lock=True)
def spec_obj() -> ta.Any:
    return json.loads(spec_src())


@lang.cached_function(lock=True)
def spec_json_schema() -> js.Keywords:
    return js.KeywordParser(
        allow_unknown='x-only',
        allow_specific_unknowns={'discriminator'},
    ).parse_keywords(spec_obj())


##


class Cli(ap.Cli):
    @ap.cmd()
    def path(self) -> None:
        print(spec_path())

    @ap.cmd(
        ap.arg('--raw', action='store_true'),
    )
    def dump(self) -> None:
        if self.args.raw:
            print(spec_src())
        else:
            print(json.dumps_pretty(spec_json_schema().render()))

    @ap.cmd(
        ap.arg('-W', '--write', action='store_true'),
    )
    def gen(self) -> None:
        from omdev.specs.jsonschema.codegen import JsonSchemaCodeGen

        gen = JsonSchemaCodeGen(spec_json_schema())
        src = gen.gen_module()

        if self.args.write:
            out_path = os.path.join(os.path.dirname(__file__), 'protocol.py')
            with open(out_path, 'w') as f:
                f.write(src)

        else:
            print(src)


def _main() -> None:
    Cli().cli_run()


if __name__ == '__main__':
    _main()
