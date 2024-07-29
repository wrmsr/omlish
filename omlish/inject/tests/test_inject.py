import typing as ta

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


def test_set_multi():
    es = inj.as_elements(
        inj.bind_set_provider(inj.Key(ta.AbstractSet[int])),
        inj.SetBinding(inj.Key(ta.AbstractSet[int]), inj.Key(int, tag='four twenty')),
        inj.SetBinding(inj.Key(ta.AbstractSet[int]), inj.Key(int, tag='four twenty one')),
        inj.Binding(inj.Key(int, tag='four twenty'), inj.const(420)),
        inj.Binding(inj.Key(int, tag='four twenty one'), inj.const(421)),
    )

    i = inj.create_injector(es)
    assert i.provide(inj.Key(ta.AbstractSet[int])) == {420, 421}


def test_map_multi():
    es = inj.as_elements(
        inj.bind_map_provider(inj.Key(ta.Mapping[str, int])),
        inj.MapBinding(inj.Key(ta.Mapping[str, int]), 'a', inj.Key(int, tag='four twenty')),
        inj.MapBinding(inj.Key(ta.Mapping[str, int]), 'b', inj.Key(int, tag='four twenty one')),
        inj.Binding(inj.Key(int, tag='four twenty'), inj.const(420)),
        inj.Binding(inj.Key(int, tag='four twenty one'), inj.const(421)),
    )

    i = inj.create_injector(es)
    assert i.provide(inj.Key(ta.Mapping[str, int])) == {'a': 420, 'b': 421}


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
