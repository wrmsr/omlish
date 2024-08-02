import typing as ta

from ... import inject as inj


def test_set_multi():
    es = inj.as_elements(
        inj.bind_set_provider(ta.AbstractSet[int]),

        inj.bind(420, tag='four twenty'),
        inj.SetBinding(inj.as_key(ta.AbstractSet[int]), inj.Key(int, tag='four twenty')),

        inj.bind(421, tag='four twenty one'),
        inj.SetBinding(inj.as_key(ta.AbstractSet[int]), inj.Key(int, tag='four twenty one')),
    )

    i = inj.create_injector(es)
    assert i.provide(inj.as_key(ta.AbstractSet[int])) == {420, 421}


def test_map_multi():
    es = inj.as_elements(
        inj.bind_map_provider(ta.Mapping[str, int]),

        inj.bind(420, tag='four twenty'),
        inj.MapBinding(inj.as_key(ta.Mapping[str, int]), 'a', inj.Key(int, tag='four twenty')),

        inj.bind(421, tag='four twenty one'),
        inj.MapBinding(inj.as_key(ta.Mapping[str, int]), 'b', inj.Key(int, tag='four twenty one')),
    )

    i = inj.create_injector(es)
    assert i.provide(inj.as_key(ta.Mapping[str, int])) == {'a': 420, 'b': 421}
