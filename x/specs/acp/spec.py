"""
blob/5ecc39d682b6e5d3da99706a286a9533f5664882/docs/spec/openapi.yaml
"""
import os.path

from omdev.cache import data as dcache
from omlish import marshal as msh
from omlish.formats import json
from omlish.formats import yaml
from omlish.specs import openapi


##


ACP_SPEC_DATA = dcache.GitSpec(
    'https://github.com/i-am-bee/acp/',
    rev='5ecc39d682b6e5d3da99706a286a9533f5664882',
    subtrees=[
        'docs/spec/openapi.yaml',
    ],
)


def _main() -> None:
    spec_dir = dcache.default().get(ACP_SPEC_DATA)

    with open(os.path.join(spec_dir, 'docs/spec/openapi.yaml')) as f:
        spec_content = yaml.safe_load(f)

    spec: openapi.Openapi = msh.unmarshal(spec_content, openapi.Openapi)

    print(json.dumps_pretty(msh.marshal(spec)))


if __name__ == '__main__':
    _main()
