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

[tool.omlish.pyproject.venvs.all]
interp = '@12'
requires = ['requirements-dev.txt']
srcs = ['@main']

[tool.omlish.pyproject.venvs.default]
requires = ['requirements-ext.txt']

[tool.omlish.pyproject.venvs.'13']
interp = '@13'

[tool.omlish.pyproject.venvs.'13t']
interp = '@13t'

[tool.omlish.pyproject.venvs.'11']
interp = '@11'
requires = []
srcs = []

[tool.omlish.pyproject.venvs.'10']
interp = '@10'
requires = []
srcs = []

[tool.omlish.pyproject.venvs.'9']
interp = '@9'
requires = []
srcs = []

[tool.omlish.pyproject.venvs.'8']
interp = '@8'
requires = []
srcs = []

[tool.omlish.pyproject.venvs.docker]
docker = 'omlish-dev'

[tool.omlish.pyproject.venvs.docker-amd64]
docker = 'omlish-dev-amd64'

[tool.omlish.pyproject.venvs.deploy]
interp = 'python3.12'
requires = ['requirements.txt']


[tool.omlish.pyproject.venvs.debug]
interp = '@12-debug'
"""


@dc.dataclass(frozen=True)
class VenvConfig:
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
