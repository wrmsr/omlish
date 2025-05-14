"""
https://github.com/modelcontextprotocol/modelcontextprotocol/blob/9b15ff98b87d6a6a54055f4189feb22e750d9389/schema/2025-03-26/schema.json
"""
import os.path

from omdev.cache import data as dcache
from omlish.formats import json
from omlish.specs import jsonschema as jsch


##


MCP_SPEC_VERSION = '2025-03-26'

MCP_SPEC_DATA = dcache.GitSpec(
    'https://github.com/modelcontextprotocol/modelcontextprotocol',
    rev='9b15ff98b87d6a6a54055f4189feb22e750d9389',
    subtrees=[
        f'schema/{MCP_SPEC_VERSION}/schema.json',
    ],
)


def _main() -> None:
    spec_dir = dcache.default().get(MCP_SPEC_DATA)

    with open(os.path.join(spec_dir, 'schema', MCP_SPEC_VERSION, 'schema.json')) as f:
        spec_content = json.load(f)

    spec_jsch = jsch.parse_keywords(spec_content)

    print(json.dumps_pretty(jsch.render_keywords(spec_jsch)))


if __name__ == '__main__':
    _main()
