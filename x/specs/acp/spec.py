"""
https://github.com/agentclientprotocol/agent-client-protocol/tree/main
"""
import os.path

from omdev.cache import data as dcache
from omlish.formats import json
from omlish.specs import jsonschema as js


##


ACP_SPEC_DATA = dcache.GitSpec(
    'https://github.com/agentclientprotocol/agent-client-protocol',
    rev='f21d317659af14c405716ccb3ca381482c8965e1',
    subtrees=[
        ACP_SPEC_PATH := 'schema/schema.json',
    ],
)


def _main() -> None:
    spec_dir = dcache.default().get(ACP_SPEC_DATA)

    with open(os.path.join(spec_dir, ACP_SPEC_PATH)) as f:
        spec_src = f.read()

    spec_dct = json.loads(spec_src)
    spec_js = js.KeywordParser(
        allow_unknown='x-only',
        allow_specific_unknowns={'discriminator'},
    ).parse_keywords(spec_dct)

    print(spec_js)


if __name__ == '__main__':
    _main()
