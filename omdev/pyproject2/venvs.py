# ruff: noqa: UP006 UP007
import glob
import itertools
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_not_none
from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_check_call
from omlish.lite.subprocesses import subprocess_check_output

from .configs import VenvConfig


##


class Venv:
    def __init__(
            self,
            name: str,
            cfg: VenvConfig,
    ) -> None:
        super().__init__()
        self._name = name
        self._cfg = cfg

    @property
    def cfg(self) -> VenvConfig:
        return self._cfg

    DIR_NAME = '.venvs'

    @property
    def dir_name(self) -> str:
        return os.path.join(self.DIR_NAME, self._name)

    @cached_nullary
    def interp_exe(self) -> str:
        return _get_interp_exe(check_not_none(self._cfg.interp))

    @cached_nullary
    def exe(self) -> str:
        ve = os.path.join(self.dir_name, 'bin/python')
        if not os.path.isfile(ve):
            raise Exception(f'venv exe {ve} does not exist or is not a file!')
        return ve

    @cached_nullary
    def create(self) -> bool:
        if os.path.exists(dn := self.dir_name):
            if not os.path.isdir(dn):
                raise Exception(f'{dn} exists but is not a directory!')
            return False

        log.info('Using interpreter %s', (ie := self.interp_exe()))
        subprocess_check_call(ie, '-m', 'venv', dn)

        ve = self.exe()

        subprocess_check_call(
            ve,
            '-m', 'pip',
            'install', '-v', '--upgrade',
            'pip',
            'setuptools',
            'wheel',
        )

        if (sr := self._cfg.requires):
            subprocess_check_call(
                ve,
                '-m', 'pip',
                'install', '-v',
                *itertools.chain.from_iterable(['-r', r] for r in ([sr] if isinstance(sr, str) else sr)),
            )

        return True

    @staticmethod
    def _resolve_srcs(raw: ta.List[str]) -> ta.List[str]:
        out: list[str] = []
        seen: ta.Set[str] = set()
        for r in raw:
            es: list[str]
            if any(c in r for c in '*?'):
                es = list(glob.glob(r, recursive=True))
            else:
                es = [r]
            for e in es:
                if e not in seen:
                    seen.add(e)
                    out.append(e)
        return out

    @cached_nullary
    def srcs(self) -> ta.Sequence[str]:
        return self._resolve_srcs(self._cfg.srcs or [])
