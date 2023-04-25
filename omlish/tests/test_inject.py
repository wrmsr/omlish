from .. import inject as inj


def test_inject():
    bs = [
        inj.Binding(inj.Key(int), inj.SimpleProvider(int, lambda _: 420)),
    ]

    i = inj.Injector(bs)
    assert i.try_provide(inj.Key(int)) == 420
