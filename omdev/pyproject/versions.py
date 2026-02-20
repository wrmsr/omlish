# ruff: noqa: UP045
import dataclasses as dc
import json
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary


##


@dc.dataclass(frozen=True)
class VersionsFile:
    name: ta.Optional[str] = '.python-versions.json'

    @cached_nullary
    def pythons(self) -> ta.Mapping[str, str]:
        if not self.name or not os.path.exists(self.name):
            return {}
        with open(self.name) as f:
            s = f.read()
        return json.loads(s)
