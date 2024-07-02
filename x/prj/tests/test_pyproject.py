import dataclasses as dc

from .. import pyproject


@dc.dataclass()
class VenvSpec:
    name: str
    interp: str | None = None
    requires: list[str] | None = None
    docker: str | None = None


_TEST_TOML = """
[tool.omlish.pyproject.venvs]
all = { interp = "@11", requires = "requirements-dev.txt" }
default = { interp = "@11", requires = "requirements-ext.txt"  }
docker = { docker = "omlish-dev" }
docker-amd64 = { docker = "omlish-dev-amd64" }
debug = { interp = "@11-debug" }
"12" = { interp = "@12" }
"13" = { interp = "@13" }
"""


def test_specs():
    cfg = pyproject._toml_loads(_TEST_TOML)['tool']['omlish']['pyproject']
    venvs = {n: VenvSpec(name=n, **vs) for n, vs in cfg['venvs'].items()}
    print(venvs)
