"""
TODO:
 - inheritance
 - dynamic registration
 - dynamic switching (skip docker if not running, skip online if not online, ...)
"""
import dataclasses as dc
import enum
import typing as ta

import pytest

from .... import check
from .... import collections as col
from ....docker import all as docker
from ._registry import register


Configable: ta.TypeAlias = pytest.FixtureRequest | pytest.Config


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


SWITCHES_BY_NAME: ta.Mapping[str, Switch] = col.make_map_by(lambda sw: sw.name, SWITCHES, strict=True)
SWITCHES_BY_ATTR: ta.Mapping[str, Switch] = col.make_map_by(lambda sw: sw.attr, SWITCHES, strict=True)


##


SWITCH_STATE_OPT_PREFIXES: ta.Mapping[SwitchState, str] = {
    SwitchState.ENABLED: '--',
    SwitchState.DISABLED: '--no-',
    SwitchState.ONLY: '--only-',
}


def _get_obj_config(obj: Configable) -> pytest.Config:
    if isinstance(obj, pytest.Config):
        return obj
    elif isinstance(obj, pytest.FixtureRequest):
        return obj.config
    else:
        raise TypeError(obj)


def is_disabled(obj: Configable | None, name: str) -> bool:
    check.isinstance(name, str)
    check.in_(name, SWITCHES_BY_NAME)
    return obj is not None and _get_obj_config(obj).getoption(f'--no-{name}')


def skip_if_disabled(obj: Configable | None, name: str) -> None:
    if is_disabled(obj, name):
        pytest.skip(f'{name} disabled')


def get_specified_switches(obj: Configable) -> dict[Switch, SwitchState]:
    ret: dict[Switch, SwitchState] = {}
    for sw in SWITCHES:
        sts = {
            st
            for st, pfx in SWITCH_STATE_OPT_PREFIXES.items()
            if _get_obj_config(obj).getoption(pfx + sw.name)
        }
        if sts:
            if len(sts) > 1:
                raise Exception(f'Multiple switches specified for {sw.name}')
            ret[sw] = check.single(sts)
    return ret


@dc.dataclass(frozen=True)
class ItemSwitches:
    switches: frozenset[Switch]
    not_switches: frozenset[Switch]


def get_item_switches(item: pytest.Item) -> ItemSwitches:
    return ItemSwitches(
        frozenset(sw for sw in SWITCHES if sw.attr in item.keywords),
        frozenset(sw for sw in SWITCHES if ('not_' + sw.attr) in item.keywords),
    )


@register
class SwitchesPlugin:
    def pytest_addoption(self, parser):
        for sw in SWITCHES:
            parser.addoption(f'--no-{sw.name}', action='store_true', default=False, help=f'disable {sw.name} tests')
            parser.addoption(f'--{sw.name}', action='store_true', default=False, help=f'enables {sw.name} tests')
            parser.addoption(f'--only-{sw.name}', action='store_true', default=False, help=f'enables only {sw.name} tests')  # noqa

    def pytest_configure(self, config):
        for sw in SWITCHES:
            config.addinivalue_line('markers', f'{sw.attr}: mark test as {sw.attr}')
            config.addinivalue_line('markers', f'not_{sw.attr}: mark test as not {sw.attr}')

    class _States:
        def __init__(self, session: pytest.Session) -> None:
            super().__init__()

            self.session = session

            self.default_states_by_switch: dict[Switch, SwitchState] = {
                sw: sw.default_state(session)
                for sw in SWITCHES
            }

            self.states_by_switch: dict[Switch, SwitchState] = {
                **self.default_states_by_switch,
                **get_specified_switches(session.config),
            }

            self.switch_sets_by_state: dict[SwitchState, frozenset[Switch]] = {
                st: frozenset(sws)
                for st, sws in col.multi_map(
                    (st, sw)
                    for sw, st in self.states_by_switch.items()
                ).items()
            }

    _states_key: ta.ClassVar[pytest.StashKey[_States]] = pytest.StashKey[_States]()

    def pytest_sessionstart(self, session):
        session.stash[self._states_key] = self._States(session)

    def pytest_collection_modifyitems(self, config, items):
        def process_item(item):
            state: SwitchesPlugin._States = item.session.stash[self._states_key]

            item_switches = get_item_switches(item)

            for sw in item_switches.switches:
                for mk in sw.add_marks or []:
                    item.add_marker(mk)

            if (only_switches := state.switch_sets_by_state.get(SwitchState.ONLY)) is not None:
                if not any(sw in only_switches for sw in item_switches.switches):
                    item.add_marker(pytest.mark.skip(
                        reason=f'skipping switches ({tuple(sw.name for sw in item_switches.switches)!r} (only)',
                    ))
                    return

            disabled_switches = state.switch_sets_by_state.get(SwitchState.DISABLED, frozenset())
            for sw in item_switches.switches:
                if sw in disabled_switches:
                    item.add_marker(pytest.mark.skip(reason=f'skipping switch {sw.name!r} (disabled)'))

            enabled_switches = state.switch_sets_by_state.get(SwitchState.ENABLED, frozenset())
            for sw in item_switches.not_switches:
                if sw in enabled_switches:
                    item.add_marker(pytest.mark.skip(reason=f'skipping switch {sw.name!r} (not-enabled)'))

        for item in items:
            process_item(item)

    def pytest_collection_finish(self, session):
        state: SwitchesPlugin._States = session.stash[self._states_key]

        if_single_switches = state.switch_sets_by_state.get(SwitchState.IF_SINGLE, frozenset())

        if len(session.items) > 1:
            for item in session.items:
                item_switches = get_item_switches(item)
                for sw in item_switches.switches:
                    if sw in if_single_switches:
                        item.add_marker(pytest.mark.skip(reason=f'skipping switch {sw.name!r} (not-single)'))
