import dataclasses as dc

import pytest

from ... import inject as inj
from ... import lang


def test_inject():
    i = inj.create_injector(
        inj.bind(420),
        inj.bind(lang.typed_lambda(str, i=int)(lambda i: str(i))),
    )
    assert i.provide(int) == 420
    assert i.provide(str) == '420'


def test_default():
    @dc.dataclass(frozen=True)
    class Foo:
        i: int
        s: str = 'hi'

    assert inj.create_injector(inj.bind(420), inj.bind(Foo))[Foo] == Foo(420)
    assert inj.create_injector(inj.bind(420), inj.bind('bye'), inj.bind(Foo))[Foo] == Foo(420, 'bye')


def test_optional():
    def f(i: int, f: float | None = None) -> str:
        return f'{i=} {f=}'

    es = inj.as_elements(
        inj.bind(420),
        inj.bind(f),
    )
    assert inj.create_injector(es)[str] == 'i=420 f=None'

    es = inj.as_elements(
        inj.bind(2.3),
        *es,
    )
    assert inj.create_injector(es)[str] == 'i=420 f=2.3'


def test_dupe_squashing():
    i = inj.create_injector(
        inj.as_elements(
            inj.bind(420),
            inj.bind(42.),
        ),
        inj.as_elements(
            inj.bind(420),
            inj.bind('four twenty'),
        ),
    )
    assert i[int] == 420
    assert i[float] == 42.
    assert i[str] == 'four twenty'

    with pytest.raises(inj.ConflictingKeyError):
        inj.create_injector(
            inj.as_elements(
                inj.bind(420),
                inj.bind(42.),
            ),
            inj.as_elements(
                inj.bind(421),
                inj.bind('four twenty'),
            ),
        )
