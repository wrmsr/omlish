"""
TODO:
 - no config, explicit opt-in allowing a cyclic proxy for a specific type, bind a CyclicProxyProvider or smth
"""
import dataclasses as dc

import pytest

from ... import inject as inj


@dc.dataclass()
class CycA:
    b: 'CycB'


@dc.dataclass()
class CycB:
    a: CycA


def test_cyclic_exc():
    injector = inj.create_injector(
        inj.bind(CycA, singleton=True),
        inj.bind(CycB, singleton=True),
    )
    with pytest.raises(inj.CyclicDependencyError):  # noqa
        a = injector[CycA]  # noqa
        b = injector[CycB]  # noqa


# FIXME:
# def test_cyclic_prox():
#     binder = bind_.create_binder()
#     binder.bind_class(CycA, as_singleton=True)
#     binder.bind_class(CycB, as_singleton=True)
#     injector = inj.create_injector(binder, config=inj.InjectorConfig(enable_cyclic_proxies=True))
#     a = injector[CycA]
#     b = injector[CycB]
#     a.x = 5
#     b.y = 10
#     assert a.b is b
#     assert b.a is not a
#     assert b.a.b is b
#     assert a.b.a is not a
#     assert a.b.y == 10
#     assert b.a.x == 5
