import dataclasses as dc
import typing as ta

from ... import inject as inj


def test_set_multi():
    i = inj.create_injector(
        inj.bind(420, tag='four twenty'),
        inj.set_binder[int]().bind(inj.Key(int, tag='four twenty')),

        inj.bind(421, tag='four twenty one'),
        inj.set_binder[int]().bind(inj.Key(int, tag='four twenty one')),
    )
    assert i.provide(inj.Key(ta.AbstractSet[int])) == {420, 421}


def test_map_multi():
    i = inj.create_injector(
        inj.bind(420, tag='four twenty'),
        inj.map_binder[str, int]().bind('a', inj.Key(int, tag='four twenty')),

        inj.bind(421, tag='four twenty one'),
        inj.map_binder[str, int]().bind('b', inj.Key(int, tag='four twenty one')),
    )
    assert i.provide(inj.Key(ta.Mapping[str, int])) == {'a': 420, 'b': 421}


def test_private_multis():
    i = inj.create_injector(
        inj.private(
            inj.bind('a!'),
            inj.bind(str, tag='a', to_key=str, expose=True),
        ),
        inj.private(
            inj.bind('b!'),
            inj.bind(str, tag='b', to_key=str, expose=True),
        ),
        inj.set_binder[str]().bind(inj.Key(str, tag='a')),
        inj.set_binder[str]().bind(inj.Key(str, tag='b')),
    )
    assert set(i[ta.AbstractSet[str]]) == {'a!', 'b!'}


def test_bind_set_entry_const():
    @dc.dataclass(frozen=True)
    class Foo:
        s: str

    injector = inj.create_injector(
        inj.set_binder[Foo](),

        inj.bind_set_entry_const(ta.AbstractSet[Foo], Foo('abc')),
        inj.bind_set_entry_const(ta.AbstractSet[Foo], Foo('def')),
    )
    assert set(injector[ta.AbstractSet[Foo]]) == {Foo('abc'), Foo('def')}


def test_bind_map_entry_const():
    @dc.dataclass(frozen=True)
    class Foo:
        s: str

    injector = inj.create_injector(
        inj.map_binder[str, Foo](),

        inj.bind_map_entry_const(ta.Mapping[str, Foo], 'abc', Foo('def')),
        inj.bind_map_entry_const(ta.Mapping[str, Foo], 'ghi', Foo('jkl')),
    )
    assert dict(injector[ta.Mapping[str, Foo]]) == {'abc': Foo('def'), 'ghi': Foo('jkl')}
