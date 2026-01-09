# ruff: noqa: UP045
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary


##


@dc.dataclass(frozen=True)
class VersionsFile:
    name: ta.Optional[str] = '.versions'

    @staticmethod
    def parse(s: str) -> ta.Mapping[str, str]:
        return {
            k: v
            for l in s.splitlines()
            if (sl := l.split('#')[0].strip())
            for k, _, v in (sl.partition('='),)
        }

    @cached_nullary
    def contents(self) -> ta.Mapping[str, str]:
        if not self.name or not os.path.exists(self.name):
            return {}
        with open(self.name) as f:
            s = f.read()
        return self.parse(s)

    @staticmethod
    def get_pythons(d: ta.Mapping[str, str]) -> ta.Mapping[str, str]:
        pfx = 'PYTHON_'
        return {k[len(pfx):].lower(): v for k, v in d.items() if k.startswith(pfx)}

    @cached_nullary
    def pythons(self) -> ta.Mapping[str, str]:
        return self.get_pythons(self.contents())
