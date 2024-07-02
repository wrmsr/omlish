import dataclasses as dc
import os.path
import subprocess
import sys

from .. import pyproject


@dc.dataclass()
class VenvSpec:
    name: str
    interp: str | None = None
    requires: list[str] | None = None
    docker: str | None = None


def get_interp_exe(s: str) -> str:
    if not s.startswith('@'):
        return s
    raw_vers = pyproject._read_versions_file()  # noqa
    pfx = 'PYTHON_'
    vers = {k[len(pfx):].lower(): v for k, v in raw_vers.items() if k.startswith(pfx)}
    ver = vers[s[1:]]
    interp_script = 'omdev/scripts/interp.py'
    exe = subprocess.check_output([sys.executable, interp_script, 'resolve', ver]).decode().strip()
    return exe


class Venv:
    def __init__(self, spec: VenvSpec) -> None:
        super().__init__()
        self._spec = spec

    @property
    def spec(self) -> VenvSpec:
        return self._spec

    @pyproject.cached_nullary
    def interp_exe(self) -> str:
        return get_interp_exe(self._spec.interp)


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

    venvs = {n: Venv(vs) for n, vs in venv_specs.items()}
    print(venvs['12'].interp_exe())
