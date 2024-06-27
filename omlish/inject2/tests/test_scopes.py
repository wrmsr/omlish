from ... import inject2 as inj


def test_scopes():
    ss = inj.SeededScope('hi')
    i = inj.create_injector(inj.as_elements(
        inj.bind_scope(ss),
        inj.in_(420, ss),
    ))
    with i.provide(inj.Key(inj.SeededScope.Manager, tag=ss))({}):
        assert i[int] == 420
