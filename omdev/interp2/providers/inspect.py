# ruff: noqa: UP006
import dataclasses as dc
import json
import typing as ta

from ...amalg.std.subprocesses import subprocess_check_output
from ...amalg.std.versions.versions import Version
from ...amalg.std.versions.versions import parse_version


@dc.dataclass(frozen=True)
class InterpInspection:
    exe: str
    version: Version

    version_str: str
    config_vars: ta.Mapping[str, str]
    prefix: str
    base_prefix: str

    @property
    def debug(self) -> bool:
        return bool(self.config_vars.get('Py_DEBUG'))

    @property
    def threaded(self) -> bool:
        return bool(self.config_vars.get('Py_GIL_DISABLED'))

    @property
    def is_venv(self) -> bool:
        return self.prefix != self.base_prefix


class InterpInspector:

    def __init__(self) -> None:
        super().__init__()

        self._cache: ta.Dict[str, InterpInspection] = {}

    _RAW_INSPECTION_CODE = """
    __import__('json').dumps(dict(
        version_str=__import__('sys').version,
        prefix=__import__('sys').prefix,
        base_prefix=__import__('sys').base_prefix,
        config_vars=__import__('sysconfig').get_config_vars(),
    ))"""

    _INSPECTION_CODE = ''.join(l.strip() for l in _RAW_INSPECTION_CODE.splitlines())

    def _build_inspection(
            self,
            exe: str,
            output: str,
    ) -> InterpInspection:
        dct = json.loads(output)

        version = parse_version(dct['version'].split()[0])

        return InterpInspection(
            exe=exe,
            version=version,
            **{k: dct[k] for k in (
                'version_str',
                'prefix',
                'base_prefix',
                'config_vars',
            )},
        )

    def _inspect(self, exe: str) -> InterpInspection:
        output = subprocess_check_output(exe, '-c', f'print({self._INSPECTION_CODE})')
        return self._build_inspection(exe, output.decode())

    def inspect(self, exe: str) -> InterpInspection:
        try:
            return self._cache[exe]
        except KeyError:
            ret = self._cache[exe] = self._inspect(exe)
            return ret


INTERP_INSPECTOR = InterpInspector()
