from .. import pyproject


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
    run = pyproject.Run(
        raw_cfg=_TEST_TOML,
    )

    venv = run.venvs()['12']
    # venv.create()  # FIXME
    assert venv
