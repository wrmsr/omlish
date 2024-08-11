import json
import shutil
import typing as ta

from .subprocesses import subprocess_check_call
from .subprocesses import subprocess_check_output


def toml_loads(s: str) -> ta.Any:
    toml: ta.Any = None
    try:
        import tomllib as toml
    except ImportError:
        try:
            mod = __import__('pip._vendor.tomli')
        except ImportError:
            pass
        else:
            toml = mod._vendor.tomli  # noqa
    if toml is not None:
        return toml.loads(s)

    if shutil.which('toml2json') is None:
        subprocess_check_call(['cargo', 'install', 'toml2json'])
    jsonb = subprocess_check_output(['toml2json'], input=s.encode())

    return json.loads(jsonb.decode().strip())
