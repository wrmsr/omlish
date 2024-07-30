from .. import sync


def test_lazy_fn():
    c = 0

    def fn():
        nonlocal c
        c += 1
        return 420

    lfn = sync.LazyFn(fn)

    assert c == 0
    assert lfn.get() == 420
    assert c == 1
    assert lfn.get() == 420
    assert c == 1
