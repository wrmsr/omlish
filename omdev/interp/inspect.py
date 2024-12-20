# ruff: noqa: UP006 UP007
import dataclasses as dc
import json
import logging
import sys
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses

from ..packaging.versions import Version
from .types import InterpOpts
from .types import InterpVersion


@dc.dataclass(frozen=True)
class InterpInspection:
    exe: str
    version: Version

    version_str: str
    config_vars: ta.Mapping[str, str]
    prefix: str
    base_prefix: str

    @property
    def opts(self) -> InterpOpts:
        return InterpOpts(
            threaded=bool(self.config_vars.get('Py_GIL_DISABLED')),
            debug=bool(self.config_vars.get('Py_DEBUG')),
        )

    @property
    def iv(self) -> InterpVersion:
        return InterpVersion(
            version=self.version,
            opts=self.opts,
        )

    @property
    def is_venv(self) -> bool:
        return self.prefix != self.base_prefix


class InterpInspector:
    def __init__(
            self,
            *,
            log: ta.Optional[logging.Logger] = None,
    ) -> None:
        super().__init__()

        self._log = log

        self._cache: ta.Dict[str, ta.Optional[InterpInspection]] = {}

    _RAW_INSPECTION_CODE = """
    __import__('json').dumps(dict(
        version_str=__import__('sys').version,
        prefix=__import__('sys').prefix,
        base_prefix=__import__('sys').base_prefix,
        config_vars=__import__('sysconfig').get_config_vars(),
    ))"""

    _INSPECTION_CODE = ''.join(l.strip() for l in _RAW_INSPECTION_CODE.splitlines())

    @staticmethod
    def _build_inspection(
            exe: str,
            output: str,
    ) -> InterpInspection:
        dct = json.loads(output)

        version = Version(dct['version_str'].split()[0])

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

    @classmethod
    def running(cls) -> 'InterpInspection':
        return cls._build_inspection(sys.executable, eval(cls._INSPECTION_CODE))  # noqa

    async def _inspect(self, exe: str) -> InterpInspection:
        output = await asyncio_subprocesses.check_output(exe, '-c', f'print({self._INSPECTION_CODE})', quiet=True)
        return self._build_inspection(exe, output.decode())

    async def inspect(self, exe: str) -> ta.Optional[InterpInspection]:
        try:
            return self._cache[exe]
        except KeyError:
            ret: ta.Optional[InterpInspection]
            try:
                ret = await self._inspect(exe)
            except Exception as e:  # noqa
                if self._log is not None and self._log.isEnabledFor(logging.DEBUG):
                    self._log.exception('Failed to inspect interp: %s', exe)
                ret = None
            self._cache[exe] = ret
            return ret
