"""
TODO:
 - inheritance
 - dynamic registration
 - dynamic switching (skip docker if not running, skip online if not online, ...)
"""
import typing as ta

import pytest

from .... import check
from .... import collections as col
from ._registry import register


Configable = pytest.FixtureRequest | pytest.Config


SWITCHES = {
    'docker': True,
    'online': True,
    'integration': True,
    'slow': False,
}


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
    check.in_(name, SWITCHES)
    return obj is not None and _get_obj_config(obj).getoption(f'--no-{name}')


def skip_if_disabled(obj: Configable | None, name: str) -> None:
    if is_disabled(obj, name):
        pytest.skip(f'{name} disabled')


def get_switches(obj: Configable) -> ta.Mapping[str, SwitchState]:
    ret: dict[str, SwitchState] = {}
    for sw, d in SWITCHES.items():
        sts = {
            st
            for st, pfx in SWITCH_STATE_OPT_PREFIXES.items()
            if _get_obj_config(obj).getoption(pfx + sw)
        }
        if sts:
            if len(sts) > 1:
                raise Exception(f'Multiple switches specified for {sw}')
            ret[sw] = check.single(sts)
        else:
            ret[sw] = d
    return ret


@register
class SwitchesPlugin:

    def pytest_configure(self, config):
        for sw in SWITCHES:
            config.addinivalue_line('markers', f'{sw}: mark test as {sw}')

    def pytest_addoption(self, parser):
        for sw in SWITCHES:
            parser.addoption(f'--no-{sw}', action='store_true', default=False, help=f'disable {sw} tests')
            parser.addoption(f'--{sw}', action='store_true', default=False, help=f'enables {sw} tests')
            parser.addoption(f'--only-{sw}', action='store_true', default=False, help=f'enables only {sw} tests')

    def pytest_collection_modifyitems(self, config, items):
        sts = get_switches(config)
        stx = col.multi_map(map(reversed, sts.items()))  # type: ignore
        ts, fs, onlys = (stx.get(k, ()) for k in (True, False, 'only'))

        def process(item):
            sws = {sw for sw in SWITCHES if sw in item.keywords}

            if onlys:
                if not any(sw in onlys for sw in sws):
                    item.add_marker(pytest.mark.skip(reason=f'skipping switches {sws}'))
                    return

            else:
                for sw in sws:
                    if sw in fs:
                        item.add_marker(pytest.mark.skip(reason=f'skipping switches {sw}'))

        for item in items:
            process(item)
