import pprint

from ... import inject2 as inj
from ... import lang
from ..impl.elements import ElementCollection
from ..impl.injector import InjectorImpl


def test_inject():
    es = inj.Elements([
        inj.as_binding(420),
        inj.as_binding(lang.typed_lambda(str, i=int)(lambda i: str(i))),
    ])

    pprint.pprint(es)

    ec = ElementCollection(es)
    i = InjectorImpl(ec)
    assert i.provide(int) == 420
    assert i.provide(str) == '420'
