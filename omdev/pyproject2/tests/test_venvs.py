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

[tool.omlish.pyproject.venvs]
all = { interp = '@12', requires = 'requirements-dev.txt', srcs = ['@main'] }
default = { requires = 'requirements-ext.txt' }
'13' = { interp = '@13' }
'13t' = { interp = '@13t' }
'11' = { interp = '@11', requires = [], srcs = [] }
'10' = { interp = '@10', requires = [], srcs = [] }
'9' = { interp = '@9', requires = [], srcs = [] }
'8' = { interp = '@8', requires = [], srcs = [] }
docker = { docker = 'omlish-dev' }
docker-amd64 = { docker = 'omlish-dev-amd64' }
deploy = { interp = 'python3.12', requires = 'requirements.txt' }
debug = { interp = '@12-debug' }
"""


class TestVenvs(unittest.TestCase):
    def test_venvs(self):
        dct = toml_loads(_TEST_TOML)
        print(dct)
