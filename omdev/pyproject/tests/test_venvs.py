import json
import unittest

from omcore.formats.toml.parser import toml_loads
from omcore.lite.marshal import marshal_obj

from ..configs import PyprojectConfigPreparer


_TEST_TOML = """
[tool.om.pyproject.srcs]
main = [
    'omcore',
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

[tool.om.pyproject.venvs._default]
interp = '@13'
requires = ['requirements-dev.txt']
srcs = ['@main']

[tool.om.pyproject.venvs.default]
inherits = ['_default']
requires = ['requirements-ext.txt']

[tool.om.pyproject.venvs.'13t']
inherits = ['_default']
interp = '@13t'

[tool.om.pyproject.venvs._old]
requires = []
srcs = []

[tool.om.pyproject.venvs.'12']
inherits = ['_old']
interp = '@12'

[tool.om.pyproject.venvs.'11']
inherits = ['_old']
interp = '@11'

[tool.om.pyproject.venvs.'10']
inherits = ['_old']
interp = '@10'

[tool.om.pyproject.venvs.'9']
inherits = ['_old']
interp = '@9'

[tool.om.pyproject.venvs.'8']
inherits = ['_old']
interp = '@8'

[tool.om.pyproject.venvs.docker]
inherits = ['_default']
docker_service = 'omlish-dev'

[tool.om.pyproject.venvs.docker-amd64]
inherits = ['_default']
docker_service = 'omlish-dev-amd64'

[tool.om.pyproject.venvs.deploy]
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

        dct = toml_loads(_TEST_TOML)['tool']['om']['pyproject']
        pj(dct)

        pcfg = PyprojectConfigPreparer(
            python_versions=_TEST_VERSIONS_FILE,
        ).prepare_config(dct)

        pj(marshal_obj(pcfg))
