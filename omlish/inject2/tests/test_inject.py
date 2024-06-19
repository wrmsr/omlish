import pprint

from ... import inject2 as inj
from ..impl.elements import ElementCollection
from ..impl.injector import InjectorImpl


def test_inject():
    es = inj.Elements([
        inj.as_binding(420),
    ])

    pprint.pprint(es)

    ec = ElementCollection(es)
    i = InjectorImpl(ec)
    assert i.provide(int) == 420
