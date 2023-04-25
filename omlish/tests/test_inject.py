from .. import inject as inj


def test_inject():
    bs = [
        inj._as_binding(420),
    ]

    i = inj.Injector(bs)
    assert i.try_provide(inj.Key(int)) == 420
