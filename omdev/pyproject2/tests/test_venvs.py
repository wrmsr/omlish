import dataclasses as dc
import unittest
import typing as ta

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

[tool.omlish.pyproject.venvs]
all = { interp = '@12', requires = ['requirements-dev.txt'], srcs = ['@main'] }
default = { requires = ['requirements-ext.txt'] }
'13' = { interp = '@13' }
'13t' = { interp = '@13t' }
'11' = { interp = '@11', requires = [], srcs = [] }
'10' = { interp = '@10', requires = [], srcs = [] }
'9' = { interp = '@9', requires = [], srcs = [] }
'8' = { interp = '@8', requires = [], srcs = [] }
docker = { docker = 'omlish-dev' }
docker-amd64 = { docker = 'omlish-dev-amd64' }
deploy = { interp = 'python3.12', requires = ['requirements.txt'] }
debug = { interp = '@12-debug' }
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
        print(dct)
