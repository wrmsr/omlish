# ruff: noqa: UP006 UP007
import os.path
import typing as ta

from ..amalg.std.cached import cached_nullary


class VenvInterps:
    def __init__(
            self,
            *,
            versions_file: str | None = '.versions',
    ) -> None:
        super().__init__()

        self._versions_file = versions_file

    @cached_nullary
    def read_versions_file(self) -> ta.Mapping[str, str]:
        if not self._versions_file or not os.path.exists(self._versions_file):
            return {}
        with open(self._versions_file) as f:
            lines = f.readlines()
        return {
            k: v
            for l in lines
            if (sl := l.split('#')[0].strip())
            for k, _, v in (sl.partition('='),)
        }

    @cached_nullary
    def versions_file_pythons(self) -> ta.Mapping[str, str]:
        raw_vers = self.read_versions_file()
        pfx = 'PYTHON_'
        return {k[len(pfx):].lower(): v for k, v in raw_vers.items() if k.startswith(pfx)}
