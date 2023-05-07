import dataclasses as dc
import typing as ta

import pytest

from ... import bind as bnd
from .... import lang
from ....dev.pytest.plugins import ci
from ....dev.pytest.plugins import switches
from .harness import FixtureRequest
from .harness import register
from .harness import Session


@dc.dataclass(frozen=True)
class Ci(lang.Final):
    value: bool

    def __bool__(self) -> bool:
        return self.value

    def skip_if(self) -> None:
        if self:
            pytest.skip('ci disabled')


class Switches(lang.Final):

    def __init__(self, values: ta.Mapping[str, bool]) -> None:
        super().__init__()

        self._values = dict(values)

    def __getitem__(self, name: str) -> bool:
        return self._values[name]

    def skip_if_not(self, name: str) -> None:
        if self[name]:
            pytest.skip(f'{name} disabled')


def _provide_ci() -> Ci:
    return Ci(ci.is_ci())


def _provide_switches(request: FixtureRequest) -> Switches:
    return Switches(switches.get_switches(request))


binder = bnd.create_binder()
binder.bind_callable(_provide_ci, in_=Session)
binder.bind_callable(_provide_switches, in_=Session)
register(binder)
