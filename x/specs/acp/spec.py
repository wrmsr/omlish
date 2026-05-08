"""
https://github.com/agentclientprotocol/agent-client-protocol/tree/main
"""
import os.path
import typing as ta

from omlish import lang
from omdev.cache import data as dcache
from omlish.argparse import all as ap
from omlish.formats import json
from omlish.specs import jsonschema as js

from .codegen import JsonSchemaCodeGen


##


ACP_SPEC_DATA = dcache.GitSpec(
    'https://github.com/agentclientprotocol/agent-client-protocol',
    rev='f21d317659af14c405716ccb3ca381482c8965e1',
    subtrees=[
        ACP_SPEC_PATH := 'schema/schema.json',
    ],
)


@lang.cached_function(lock=True)
def spec_src() -> str:
    spec_dir = dcache.default().get(ACP_SPEC_DATA)
    with open(os.path.join(spec_dir, ACP_SPEC_PATH)) as f:
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
