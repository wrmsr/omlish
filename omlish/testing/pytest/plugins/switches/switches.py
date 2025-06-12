import dataclasses as dc
import enum
import typing as ta

import pytest

from ..... import check
from ..... import collections as col
from .....docker import all as docker


##


class SwitchState(enum.Enum):
    ENABLED = enum.auto()
    DISABLED = enum.auto()
    ONLY = enum.auto()
    IF_SINGLE = enum.auto()


@dc.dataclass(frozen=True, eq=False)
class Switch:
    name: str
    _default_state: SwitchState | ta.Callable[[pytest.Session], SwitchState]

    _: dc.KW_ONLY

    add_marks: ta.Sequence[ta.Any] | None = None

    def default_state(self, session: pytest.Session) -> SwitchState:
        if isinstance(e := self._default_state, SwitchState):
            return e
        elif callable(e):
            return check.isinstance(e(session), SwitchState)
        else:
            raise TypeError(e)

    @property
    def attr(self) -> str:
        return self.name.replace('-', '_')


##


SWITCHES: ta.Sequence[Switch] = [
    Switch(
        'name',
        lambda _: SwitchState.ENABLED if docker.has_cli() else SwitchState.DISABLED,
    ),

    Switch(
        'docker-guest',
        lambda _: SwitchState.ENABLED if docker.is_likely_in_docker() else SwitchState.DISABLED,
    ),

    Switch(
        'online',
        SwitchState.ENABLED,
    ),

    Switch(
        'integration',
        SwitchState.ENABLED,
    ),

    Switch(
        'high-mem',
        SwitchState.ENABLED,
        add_marks=[
            # https://pytest-xdist.readthedocs.io/en/latest/distribution.html
            pytest.mark.xdist_group('high-mem'),
            pytest.mark.gc_collect_after(),
        ],
    ),

    Switch(
        'slow',
        SwitchState.IF_SINGLE,
    ),
]


##


SWITCHES_BY_NAME: ta.Mapping[str, Switch] = col.make_map_by(lambda sw: sw.name, SWITCHES, strict=True)
SWITCHES_BY_ATTR: ta.Mapping[str, Switch] = col.make_map_by(lambda sw: sw.attr, SWITCHES, strict=True)
