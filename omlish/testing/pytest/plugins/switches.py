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


SWITCHES = col.OrderedSet([
    'online',
    'slow',
])


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


def get_switches(obj: Configable) -> ta.Mapping[str, bool]:
    return {
        sw: _get_obj_config(obj).getoption(f'--no-{sw}')
        for sw in SWITCHES
    }


@register
class SwitchesPlugin:

    def pytest_addoption(self, parser):
        for sw in SWITCHES:
            parser.addoption(f'--no-{sw}', action='store_true', default=False, help=f'disable {sw} tests')

    def pytest_collection_modifyitems(self, config, items):
        for sw in SWITCHES:
            if not config.getoption(f'--no-{sw}'):
                continue
            skip = pytest.mark.skip(reason=f'omit --no-{sw} to run')
            for item in items:
                if sw in item.keywords:
                    item.add_marker(skip)

    def pytest_configure(self, config):
        for sw in SWITCHES:
            config.addinivalue_line('markers', f'{sw}: mark test as {sw}')
