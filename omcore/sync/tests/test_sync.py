from ..funcs import SyncLazyFn


def test_lazy_fn():
    c = 0

    def fn():
        nonlocal c
        c += 1
        return 420

    lfn = SyncLazyFn(fn)

    assert c == 0
    assert lfn.get() == 420
    assert c == 1
    assert lfn.get() == 420
    assert c == 1
