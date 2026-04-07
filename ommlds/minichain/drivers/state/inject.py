import typing as ta

from omlish import inject as inj
from omlish import orm

from .configs import StateConfig
from .impl import DriverStateManagerImpl
from .manager import DriverStateManager
from .models import driver_state_mapper


##


def bind_state(cfg: StateConfig = StateConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind_set_entry_const(ta.AbstractSet[orm.Mapper], driver_state_mapper()),
    ])

    #

    els.extend([
        inj.bind(DriverStateManagerImpl, singleton=True),
        inj.bind(DriverStateManager, to_key=DriverStateManagerImpl),
    ])

    #

    return inj.as_elements(*els)
