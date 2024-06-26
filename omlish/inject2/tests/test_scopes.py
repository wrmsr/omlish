from ... import inject2 as inj


def test_scopes():
    foo = ScopeTag('foo')
    i = create_injector(bind(
        bind_scope(foo),
        scoped(foo, 420),
    ))
    i.provide(foo._scope_key).open({})
    assert i[int] == 420


def test_scope_seed():
    foo = ScopeTag('foo')
    i = create_injector(bind(
        bind_scope(foo),
        scoped(foo, lang.typed_lambda(str, x=int)(lambda x: str(x))),
        bind_scope_seeds(foo, int)
    ))
    i.provide(foo._scope_key).open({
        as_key(int): 420,
    })
    assert i[int] == 420
    assert i[str] == '420'
