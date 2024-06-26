from ... import inject2 as inj


def test_scopes():
    from ..impl.scopes import SeededScopeImpl

    ss = inj.SeededScope('hi')
    ssi = SeededScopeImpl(ss)
    ssk = inj.Key(SeededScopeImpl, tag=ss)
    i = inj.create_injector(inj.as_elements(
        inj.Binding(ssk, inj.as_provider(ssi)),
        inj.in_(420, ss),
    ))
    assert i.provide(ssk) is ssi
    assert i[int] == 420


# def test_scope_seed():
#     foo = ScopeTag('foo')
#     i = create_injector(bind(
#         bind_scope(foo),
#         scoped(foo, lang.typed_lambda(str, x=int)(lambda x: str(x))),
#         bind_scope_seeds(foo, int)
#     ))
#     i.provide(foo._scope_key).open({
#         as_key(int): 420,
#     })
#     assert i[int] == 420
#     assert i[str] == '420'
