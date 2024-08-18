# ruff: noqa: UP006 UP007
import dataclasses as dc
import glob
import itertools
import os.path
import sys
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_not_none
from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_check_call
from omlish.lite.subprocesses import subprocess_check_output


##


# out: list[str] = []
# seen.clear()
# for r in raw:
#     es: list[str]
#     if any(c in r for c in '*?'):
#         es = list(glob.glob(r, recursive=True))
#     else:
#         es = [r]
#     for e in es:
#         if e not in seen:
#             seen.add(e)
#             out.append(e)
# return out


##


@dc.dataclass()
class VenvSpec:
    name: str
    interp: ta.Optional[str] = None
    requires: ta.Union[str, ta.List[str], None] = None
    docker: ta.Optional[str] = None
    srcs: ta.Union[str, ta.List[str], None] = None


def build_venv_specs(cfgs: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, VenvSpec]:
    venv_specs = {n: VenvSpec(name=n, **vs) for n, vs in cfgs.items()}
    if (all_venv_spec := venv_specs.pop('all')) is not None:
        avkw = dc.asdict(all_venv_spec)
        for n, vs in list(venv_specs.items()):
            vskw = {**avkw, **{k: v for k, v in dc.asdict(vs).items() if v is not None}}
            venv_specs[n] = VenvSpec(**vskw)
    return venv_specs


class Venv:
    def __init__(
            self,
            spec: VenvSpec,
            *,
            src_aliases: ta.Optional[ta.Mapping[str, ta.Sequence[str]]] = None,
    ) -> None:
        if spec.name == 'all':
            raise Exception
        super().__init__()
        self._spec = spec
        self._src_aliases = src_aliases

    @property
    def spec(self) -> VenvSpec:
        return self._spec

    DIR_NAME_PREFIX = '.venv'
    DIR_NAME_SEP = '-'

    @property
    def dir_name(self) -> str:
        if (n := self._spec.name) == 'default':
            return self.DIR_NAME_PREFIX
        return ''.join([self.DIR_NAME_PREFIX, self.DIR_NAME_SEP, n])

    @cached_nullary
    def interp_exe(self) -> str:
        return _get_interp_exe(check_not_none(self._spec.interp))

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

        if (sr := self._spec.requires):
            subprocess_check_call(
                ve,
                '-m', 'pip',
                'install', '-v',
                *itertools.chain.from_iterable(['-r', r] for r in ([sr] if isinstance(sr, str) else sr)),
            )

        return True

    @cached_nullary
    def srcs(self) -> ta.Sequence[str]:
        return _resolve_srcs(self._spec.srcs or [], self._src_aliases or {})
