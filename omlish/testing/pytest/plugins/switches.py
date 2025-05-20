"""
TODO:
 - inheritance
 - dynamic registration
 - dynamic switching (skip docker if not running, skip online if not online, ...)
"""
import dataclasses as dc
import typing as ta

import pytest

from .... import check
from .... import collections as col
from ....docker import all as docker
from ._registry import register


Configable: ta.TypeAlias = pytest.FixtureRequest | pytest.Config


##


@dc.dataclass(frozen=True, eq=False)
class Switch:
    name: str
    _default_enabled: bool | ta.Callable[[], bool]

    _: dc.KW_ONLY

    add_marks: ta.Sequence[ta.Any] | None = None

    def default_enabled(self) -> bool:
        if isinstance(e := self._default_enabled, bool):
            return e
        elif callable(e):
            return check.isinstance(e(), bool)
        else:
            raise TypeError(e)

    @property
    def attr(self) -> str:
        return self.name.replace('-', '_')


SWITCHES: ta.Sequence[Switch] = [
    Switch(
        'name',
        docker.has_cli,
    ),

    Switch(
        'docker-guest',
        docker.is_likely_in_docker,
    ),

    Switch(
        'online',
        True,
    ),

    Switch(
        'integration',
        True,
    ),

    Switch(
        'high-mem',
        True,
        add_marks=[
            # https://pytest-xdist.readthedocs.io/en/latest/distribution.html
            pytest.mark.xdist_group('high-mem'),
        ],
    ),

    Switch(
        'slow',
        False,
    ),
]


SWITCHES_BY_NAME: ta.Mapping[str, Switch] = col.make_map_by(lambda sw: sw.name, SWITCHES, strict=True)
SWITCHES_BY_ATTR: ta.Mapping[str, Switch] = col.make_map_by(lambda sw: sw.attr, SWITCHES, strict=True)


##


SwitchState: ta.TypeAlias = bool | ta.Literal['only']

SWITCH_STATE_OPT_PREFIXES: ta.Mapping[SwitchState, str] = {
    True: '--',
    False: '--no-',
    'only': '--only-',
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


@register
class SwitchesPlugin:
    def pytest_configure(self, config):
        for sw in SWITCHES:
            config.addinivalue_line('markers', f'{sw.attr}: mark test as {sw.attr}')
            config.addinivalue_line('markers', f'not_{sw.attr}: mark test as not {sw.attr}')

    def pytest_addoption(self, parser):
        for sw in SWITCHES:
            parser.addoption(f'--no-{sw.name}', action='store_true', default=False, help=f'disable {sw.name} tests')
            parser.addoption(f'--{sw.name}', action='store_true', default=False, help=f'enables {sw.name} tests')
            parser.addoption(f'--only-{sw.name}', action='store_true', default=False, help=f'enables only {sw.name} tests')  # noqa

    def pytest_collection_modifyitems(self, config, items):
        switch_states: dict[Switch, SwitchState] = {
            **{
                sw: sw.default_enabled()
                for sw in SWITCHES
            },
            **get_specified_switches(config),
        }

        inv_switch_states: dict[SwitchState, list[Switch]] = col.multi_map((st, sw) for sw, st in switch_states.items())
        true_switches = frozenset(inv_switch_states.get(True, ()))
        false_switches = frozenset(inv_switch_states.get(False, ()))
        only_switches = frozenset(inv_switch_states.get('only', ()))

        def process(item):
            item_switches = {sw for sw in SWITCHES if sw.attr in item.keywords}
            item_not_switches = {sw for sw in SWITCHES if ('not_' + sw.attr) in item.keywords}

            for sw in item_switches:
                for mk in sw.add_marks or []:
                    item.add_marker(mk)

            if only_switches:
                if not any(sw in only_switches for sw in item_switches):
                    item.add_marker(pytest.mark.skip(reason=f'skipping switches {item_switches}'))
                    return

            for sw in item_switches:
                if sw in false_switches:
                    item.add_marker(pytest.mark.skip(reason=f'skipping switches {sw}'))

            for sw in item_not_switches:
                if sw in true_switches:
                    item.add_marker(pytest.mark.skip(reason=f'skipping switches {sw}'))

        for item in items:
            process(item)
