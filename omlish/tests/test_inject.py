from .. import inject as inj


def test_inject():
    def ifn(_):
        nonlocal ifn_n
        ifn_n += 1
        return ifn_n
    ifn_n = 0

    def sfn(_):
        nonlocal sfn_n
        sfn_n += 1
        return str(sfn_n)
    sfn_n = 0

    bs = [
        # inj._as_binding(420),
        inj.Binding(inj.Key(int), inj.FnProvider(int, ifn)),
        inj.Binding(inj.Key(str), inj.SingletonProvider(inj.FnProvider(str, sfn))),
    ]

    i = inj.Injector(bs)
    assert i.try_provide(inj.Key(int)) == 1
    assert i.try_provide(inj.Key(int)) == 2
    assert i.try_provide(inj.Key(str)) == '1'
    assert i.try_provide(inj.Key(str)) == '1'
