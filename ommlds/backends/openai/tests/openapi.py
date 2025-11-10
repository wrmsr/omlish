import os.path

from omdev.cache import data as dcache
from omlish import marshal as msh
from omlish.formats import json
from omlish.formats import yaml
from omlish.specs import openapi


##


OPENAI_OPENAPI_DATA = dcache.GitSpec(
    'https://github.com/openai/openai-openapi',
    rev='498c71ddf6f1c45b983f972ccabca795da211a3e',
    subtrees=[
        f'openapi.yaml',
    ],
)


def _main() -> None:
    api_dir = dcache.default().get(OPENAI_OPENAPI_DATA)

    with open(os.path.join(api_dir, 'openapi.yaml')) as f:
        doc = yaml.safe_load(f)
    print(json.std_backend().dumps_pretty(doc))

    api = msh.unmarshal(doc, openapi.Openapi)
    print(json.std_backend().dumps_pretty(msh.marshal(api)))


if __name__ == '__main__':
    _main()
