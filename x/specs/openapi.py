"""
https://swagger.io/specification/
"""
import dataclasses as dc
import os.path

import yaml

from omlish import marshal as msh


@dc.dataclass(frozen=True)
class Info:
    pass


@dc.dataclass(frozen=True)
class Spec:
    """https://swagger.io/specification/#openapi-object"""

    openapi: str
    info: Info


def _main():
    with open(os.path.join(os.path.dirname(__file__), '..', 'llm', 'openai.yaml')) as f:
        spec = yaml.safe_load(f)



if __name__ == '__main__':
    _main()
