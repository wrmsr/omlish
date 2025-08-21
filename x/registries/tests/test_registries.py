from ..base import RegistryLookup
from ..dicts import UniqueDictRegistry
from ..wrappers import LockedRegistry


def test_registries():
    reg0 = UniqueDictRegistry({
        'foo': 1,
        'bar': 2,
    })

    assert list(reg0['foo']) == [RegistryLookup(1, reg0)]

    reg1 = LockedRegistry(reg0)

    assert list(reg1['foo']) == [RegistryLookup(1, reg0)]
