import typing as ta

from ... import inject2 as inj
from ... import lang
from ..impl.elements import ElementCollection
from ..impl.injector import InjectorImpl


def test_inject():
    es = inj.Elements([
        inj.as_binding(420),
        inj.as_binding(lang.typed_lambda(str, i=int)(lambda i: str(i))),
    ])

    ec = ElementCollection(es)
    i = InjectorImpl(ec)
    assert i.provide(int) == 420
    assert i.provide(str) == '420'


def test_override():
    es = inj.Elements([
        inj.override(
            inj.as_binding(421),
            inj.as_binding(420),
        ),
        inj.as_binding(5.2),
        inj.as_binding(lang.typed_lambda(str, i=int, f=float)(lambda i, f: f'{i}, {f}')),
    ])

    ec = ElementCollection(es)
    i = InjectorImpl(ec)
    assert i.provide(int) == 421
    assert i.provide(str) == '421, 5.2'


def test_multi():
    es = inj.Elements([
        inj.as_(inj.multi(int), [420]),
        inj.as_(inj.multi(int), [421]),
    ])

    ec = ElementCollection(es)
    i = InjectorImpl(ec)
    assert i.provide(inj.multi(int)) == [420, 421]


def test_eager():
    c = 0

    def f() -> int:
        nonlocal c
        c += 1
        return 420

    es = inj.Elements([
        inj.as_binding(f),
        inj.eager(int),
    ])

    for _ in range(2):
        c = 0
        ec = ElementCollection(es)
        i = InjectorImpl(ec)
        assert c == 1
        assert i.provide(int) == 420
        assert c == 2


def test_optional():
    def f(i: int, f: ta.Optional[float] = None) -> str:
        return f'{i=} {f=}'

    es = inj.Elements([
        inj.as_binding(420),
        inj.as_binding(f),
    ])
    assert InjectorImpl(ElementCollection(es))[str] == 'i=420 f=None'

    es = inj.Elements([
        inj.as_binding(2.3),
        *es,
    ])
    assert InjectorImpl(ElementCollection(es))[str] == 'i=420 f=2.3'
