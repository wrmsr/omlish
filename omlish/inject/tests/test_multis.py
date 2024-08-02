import typing as ta

from ... import inject as inj


def test_set_multi():
    es = inj.as_elements(
        inj.bind(420, tag='four twenty'),
        inj.set_binder[int]().bind(inj.Key(int, tag='four twenty')),

        inj.bind(421, tag='four twenty one'),
        inj.set_binder[int]().bind(inj.Key(int, tag='four twenty one')),
    )

    i = inj.create_injector(es)
    assert i.provide(inj.Key(ta.AbstractSet[int])) == {420, 421}


def test_map_multi():
    es = inj.as_elements(
        inj.bind(420, tag='four twenty'),
        inj.map_binder[str, int]().bind('a', inj.Key(int, tag='four twenty')),

        inj.bind(421, tag='four twenty one'),
        inj.map_binder[str, int]().bind('b', inj.Key(int, tag='four twenty one')),
    )

    i = inj.create_injector(es)
    assert i.provide(inj.Key(ta.Mapping[str, int])) == {'a': 420, 'b': 421}
