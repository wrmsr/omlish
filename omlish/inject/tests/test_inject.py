from ... import inject as inj
from ... import lang


def test_inject():
    es = inj.as_elements(
        inj.as_binding(420),
        inj.as_binding(lang.typed_lambda(str, i=int)(lambda i: str(i))),
    )

    i = inj.create_injector(es)
    assert i.provide(int) == 420
    assert i.provide(str) == '420'


def test_multi():
    es = inj.as_elements(
        inj.as_(inj.set_multi(int), 420),
        inj.as_(inj.set_multi(int), 421),
    )

    i = inj.create_injector(es)
    assert sorted(i.provide(inj.set_multi(int))) == {420, 421}


def test_optional():
    def f(i: int, f: float | None = None) -> str:
        return f'{i=} {f=}'

    es = inj.as_elements(
        inj.as_binding(420),
        inj.as_binding(f),
    )
    assert inj.create_injector(es)[str] == 'i=420 f=None'

    es = inj.as_elements(
        inj.as_binding(2.3),
        *es,
    )
    assert inj.create_injector(es)[str] == 'i=420 f=2.3'
