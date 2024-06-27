from ... import inject2 as inj


def test_scopes():
    ss = inj.SeededScope('hi')
    i = inj.create_injector(inj.as_elements(
        inj.bind_scope(ss),
        inj.in_(420, ss),
        inj.bind_scope_seed(ss, float)
    ))
    with i.provide(inj.Key(inj.SeededScope.Manager, tag=ss))({
        inj.as_key(float): 4.2,
    }):
        assert i[int] == 420
        assert i[float] == 4.2
