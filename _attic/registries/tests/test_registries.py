from .. import composites as composites_
from .. import dicts as dicts_
from .. import types as types_

import pytest


def test_registries():
    reg0 = dicts_.DictRegistry()
    reg0[0] = 'zero'
    reg0[1] = 'one'
    assert reg0[0] == 'zero'
    assert reg0[1] == 'one'
    with pytest.raises(types_.NotRegisteredException):
        reg0[2]

    reg1 = dicts_.DictRegistry()
    reg1[1] = 'onex'
    reg1[2] = 'two'
    assert reg1[1] == 'onex'
    assert reg1[2] == 'two'
    with pytest.raises(types_.NotRegisteredException):
        reg1[3]

    foreg0 = composites_.CompositeRegistry([reg0, reg1], composites_.CompositeRegistry.FIRST_ONE)
    with pytest.raises(TypeError):
        foreg0[3] = 'three'
    assert foreg0[0] == 'zero'
    assert foreg0[1] == 'one'
    assert foreg0[2] == 'two'
    with pytest.raises(types_.NotRegisteredException):
        foreg0[3]

    foreg1 = composites_.CompositeRegistry([reg1, reg0], composites_.CompositeRegistry.FIRST_ONE)
    assert foreg1[0] == 'zero'
    assert foreg1[1] == 'onex'
    assert foreg1[2] == 'two'
    with pytest.raises(types_.NotRegisteredException):
        foreg1[3]

    with pytest.raises(types_.AmbiguouslyRegisteredException):
        composites_.CompositeRegistry([reg0, reg1], composites_.CompositeRegistry.ONLY_ONE)

    oreg0 = dicts_.DictRegistry()
    oreg0[0] = 'zero'
    oreg0[1] = 'one'
    oreg1 = dicts_.DictRegistry()
    oreg1[2] = 'two'
    oreg1[3] = 'three'
    ooreg = composites_.CompositeRegistry([oreg0, oreg1], composites_.CompositeRegistry.ONLY_ONE)
    assert ooreg[0] == 'zero'
    assert ooreg[1] == 'one'
    assert ooreg[2] == 'two'
    assert ooreg[3] == 'three'
    with pytest.raises(types_.NotRegisteredException):
        ooreg[4]

    dreg = dicts_.DictRegistry({'a': 'A', 'b': 'B'}, frozen=True)
    assert dreg['a'] == 'A'
    assert dreg['b'] == 'B'
    with pytest.raises(types_.NotRegisteredException):
        dreg['c']
    with pytest.raises(types_.FrozenRegistrationException):
        dreg['c'] = 'C'


def test_multi_registries():
    reg0 = dicts_.DictMultiRegistry()
    reg0[0] = {'zero'}
    reg0[1] = {'one'}
    assert reg0[0] == {'zero'}
    assert reg0[1] == {'one'}
    with pytest.raises(types_.NotRegisteredException):
        reg0[2]

    reg1 = dicts_.DictMultiRegistry()
    reg1[1] = {'onex'}
    reg1[2] = {'two'}
    assert reg1[1] == {'onex'}
    assert reg1[2] == {'two'}
    with pytest.raises(types_.NotRegisteredException):
        reg1[3]

    foreg0 = composites_.CompositeMultiRegistry([reg0, reg1], composites_.CompositeRegistry.FIRST_ONE)
    with pytest.raises(TypeError):
        foreg0[3] = {'three'}
    assert foreg0[0] == {'zero'}
    assert foreg0[1] == {'one'}
    assert foreg0[2] == {'two'}
    with pytest.raises(types_.NotRegisteredException):
        foreg0[3]

    foreg1 = composites_.CompositeMultiRegistry([reg1, reg0], composites_.CompositeRegistry.FIRST_ONE)
    assert foreg1[0] == {'zero'}
    assert foreg1[1] == {'onex'}
    assert foreg1[2] == {'two'}
    with pytest.raises(types_.NotRegisteredException):
        foreg1[3]

    foreg2 = composites_.CompositeMultiRegistry([reg1, reg0], composites_.CompositeMultiRegistry.MERGE)
    assert foreg2[0] == {'zero'}
    assert foreg2[1] == {'one', 'onex'}
    assert foreg2[2] == {'two'}
    with pytest.raises(types_.NotRegisteredException):
        foreg2[3]
