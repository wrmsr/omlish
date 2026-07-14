import typing as ta

from omcore import inject as inj
from omcore import orm

from .configs import StorageConfig
from .impl import DriverStorageManagerImpl
from .manager import DriverStorageManager
from .models import storage_mappers


##


def bind_storage(cfg: StorageConfig = StorageConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind_set_entry_const(ta.AbstractSet[orm.Mapper], m)
        for m in storage_mappers()
    ])

    #

    els.extend([
        inj.bind(DriverStorageManagerImpl, singleton=True),
        inj.bind(DriverStorageManager, to_key=DriverStorageManagerImpl),
    ])

    #

    return inj.as_elements(*els)
