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
