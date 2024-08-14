import dataclasses as dc
import json
import typing as ta
import unittest

from ...amalg.std.toml import toml_loads


_TEST_TOML = """
[tool.omlish.pyproject.srcs]
main = [
    'omlish',
    'omdev',
    'ominfra',
    'omserv',
    'app',
]

ml = [
    '@main',
    'omml',
]

all = [
    '@ml',
    'x',
]

[tool.omlish.pyproject.venvs._default]
interp = '@12'
requires = ['requirements-dev.txt']
srcs = ['@main']

[tool.omlish.pyproject.venvs.default]
inherits = ['_default']
requires = ['requirements-ext.txt']

[tool.omlish.pyproject.venvs.'13']
inherits = ['_default']
interp = '@13'

[tool.omlish.pyproject.venvs.'13t']
inherits = ['_default']
interp = '@13t'

[tool.omlish.pyproject.venvs._old]
requires = []
srcs = []

[tool.omlish.pyproject.venvs.'11']
inherits = ['_old']
interp = '@11'

[tool.omlish.pyproject.venvs.'10']
inherits = ['_old']
interp = '@10'

[tool.omlish.pyproject.venvs.'9']
inherits = ['_old']
interp = '@9'

[tool.omlish.pyproject.venvs.'8']
inherits = ['_old']
interp = '@8'

[tool.omlish.pyproject.venvs.docker]
inherits = ['_default']
docker = 'omlish-dev'

[tool.omlish.pyproject.venvs.docker-amd64]
inherits = ['_default']
docker = 'omlish-dev-amd64'

[tool.omlish.pyproject.venvs.deploy]
interp = '3.12'
requires = ['requirements.txt']
"""


@dc.dataclass(frozen=True)
class VenvConfig:
    inherits: ta.Optional[ta.Sequence[str]] = None
    interp: ta.Optional[str] = None
    requires: ta.Optional[ta.List[str]] = None
    docker: ta.Optional[str] = None
    srcs: ta.Optional[ta.List[str]] = None


@dc.dataclass(frozen=True)
class PyprojectConfig:
    srcs: ta.Mapping[str, ta.Sequence[str]]
    venvs: ta.Mapping[str, VenvConfig]


class TestVenvs(unittest.TestCase):
    def test_venvs(self):
        dct = toml_loads(_TEST_TOML)
        print(json.dumps(dct, indent=2, separators=(', ', ': ')))
