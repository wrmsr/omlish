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
default = { requires = "requirements-ext.txt"  }
docker = { docker = "omlish-dev" }
docker-amd64 = { docker = "omlish-dev-amd64" }
debug = { interp = "@11-debug" }
"12" = { interp = "@12" }
"13" = { interp = "@13" }
"""


def test_specs():
    cfg = pyproject._toml_loads(_TEST_TOML)['tool']['omlish']['pyproject']
    venv_specs = {n: VenvSpec(name=n, **vs) for n, vs in cfg['venvs'].items()}
    if (all_venv_spec := venv_specs.pop('all')) is not None:
        avkw = dc.asdict(all_venv_spec)
        for n, vs in list(venv_specs.items()):
            vskw = {**avkw, **{k: v for k, v in dc.asdict(vs).items() if v is not None}}
            venv_specs[n] = VenvSpec(**vskw)

    print(venv_specs)
