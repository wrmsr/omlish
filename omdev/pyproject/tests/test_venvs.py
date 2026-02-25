import json
import unittest

from omlish.formats.toml.parser import toml_loads
from omlish.lite.marshal import marshal_obj

from ..configs import PyprojectConfigPreparer


_TEST_TOML = """
[tool.omlish.pyproject.srcs]
main = [
    'omlish',
    'omdev',
    'ominfra',
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
interp = '@13'
requires = ['requirements-dev.txt']
srcs = ['@main']

[tool.omlish.pyproject.venvs.default]
inherits = ['_default']
requires = ['requirements-ext.txt']

[tool.omlish.pyproject.venvs.'13t']
inherits = ['_default']
interp = '@13t'

[tool.omlish.pyproject.venvs._old]
requires = []
srcs = []

[tool.omlish.pyproject.venvs.'12']
inherits = ['_old']
interp = '@12'

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
interp = '3.13'
requires = ['requirements.txt']
"""

_TEST_VERSIONS_FILE = {
    '8': '3.8.19',
    '9': '3.9.19',
    '10': '3.10.14',
    '11': '3.11.9',
    '12': '3.12.11',
    '13': '3.13.5',
    '13t': '3.13.5t',
    'dev': '3.14-dev',
}


class TestVenvs(unittest.TestCase):
    def test_venvs(self):
        def pj(o):
            print(json.dumps(o, indent=2, separators=(', ', ': ')))

        dct = toml_loads(_TEST_TOML)['tool']['omlish']['pyproject']
        pj(dct)

        pcfg = PyprojectConfigPreparer(
            python_versions=_TEST_VERSIONS_FILE,
        ).prepare_config(dct)

        pj(marshal_obj(pcfg))
