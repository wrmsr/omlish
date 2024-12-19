from ... import inject as inj


def test_scopes():
    ss = inj.SeededScope('hi')
    i = inj.create_injector(
        inj.bind_scope(ss),
        inj.bind(420, in_=ss),
        inj.bind_scope_seed(float, ss),
    )
    with inj.enter_seeded_scope(i, ss, {
        inj.as_key(float): 4.2,
    }):
        assert i[int] == 420
        assert i[float] == 4.2


def test_seeded_eager():
    c = 0

    def foo(i: int) -> str:
        nonlocal c
        c += 1
        return f'foo: {c} {i}'

    ss = inj.SeededScope('hi')
    i = inj.create_injector(
        inj.bind_scope(ss),
        inj.bind(420, in_=ss),
        inj.bind(foo, in_=ss, eager=True),
        inj.bind_scope_seed(float, ss),
    )
    assert c == 0
    with inj.enter_seeded_scope(i, ss, {
        inj.as_key(float): 4.2,
    }):
        assert c == 1
        assert i[int] == 420
        assert i[float] == 4.2
        assert i[str] == 'foo: 1 420'
