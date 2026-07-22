import gc
import threading
import weakref

import pytest

from .. import impl as impl_


def test_cache():
    c = impl_.new_cache(max_size=2)  # type: ignore
    c[0] = 'foo0'
    assert c[0] == 'foo0'
    c[1] = 'foo1'
    assert c[1] == 'foo1'
    c[2] = 'foo2'
    assert c[2] == 'foo2'
    with pytest.raises(KeyError):
        c.__getitem__(0)
    assert c[2] == 'foo2'

    c = impl_.new_cache(max_size=2)
    c[0] = 'foo0'
    assert c[0] == 'foo0'
    c[1] = 'foo1'
    assert c[1] == 'foo1'
    assert c[0] == 'foo0'
    c[2] = 'foo2'
    assert c[2] == 'foo2'
    with pytest.raises(KeyError):
        c.__getitem__(1)
    assert c[0] == 'foo0'

    c[0] = 'foo4'
    assert c[0] == 'foo4'

    del c[0]
    with pytest.raises(KeyError):
        c.__getitem__(0)


def test_weak_keys():
    class K:
        pass
    k = K()
    c = impl_.new_cache(weak_keys=True)  # type: ignore
    c[k] = 1
    assert c[k] == 1
    assert len(c) == 1
    assert list(c) == [k]
    kref = weakref.ref(K)  # noqa
    del k
    gc.collect()
    assert len(c) == 0
    assert list(c) == []


def test_weak_values():
    class V:
        pass
    c = impl_.new_cache(weak_values=True)  # type: ignore
    v = V()
    c[0] = v
    assert c[0] is v
    assert len(c) == 1
    vref = weakref.ref(v)  # noqa
    del v
    gc.collect()
    assert len(c) == 0


def test_expirey():
    clock = 0
    c = impl_.new_cache(expire_after_write=2, clock=lambda: clock)  # type: ignore
    c[0] = 'a'
    c[1] = 'b'
    clock = 1
    assert c[0] == 'a'
    clock = 3
    with pytest.raises(KeyError):
        c.__getitem__(0)


def test_identity_weak_keys_leave_no_stale_entries():
    class K:
        pass

    c = impl_.new_cache(weak_keys=True, identity_keys=True)  # type: ignore

    k = K()
    c[k] = 1
    assert c[k] == 1
    assert len(c) == 1

    del k
    gc.collect()

    assert len(c) == 0
    assert len(c._cache) == 0  # noqa


def test_iteration_order_and_reversed():
    c = impl_.new_cache()  # type: ignore
    c[1] = 'a'
    c[2] = 'b'
    c[3] = 'c'

    assert list(c) == [1, 2, 3]
    assert list(reversed(c)) == [3, 2, 1]
    assert list(c.keys()) == [1, 2, 3]
    assert list(c.items()) == [(1, 'a'), (2, 'b'), (3, 'c')]

    del c[2]

    assert list(c) == [1, 3]
    assert list(reversed(c)) == [3, 1]


def test_iteration_does_not_hold_lock():
    c = impl_.new_cache()  # type: ignore
    c[0] = 'a'
    c[1] = 'b'

    it = iter(c)
    assert next(it) == 0

    done = threading.Event()

    def other():
        c[2] = 'c'
        done.set()

    t = threading.Thread(target=other)
    t.start()
    try:
        assert done.wait(10.)
    finally:
        t.join(10.)

    # The snapshot predates the concurrent insert.
    assert list(it) == [1]
    assert list(c) == [0, 1, 2]


def test_non_positive_bounds_raise():
    with pytest.raises(ValueError):  # noqa
        impl_.new_cache(max_size=0)

    with pytest.raises(ValueError):  # noqa
        impl_.new_cache(max_size=-1)

    with pytest.raises(ValueError):  # noqa
        impl_.new_cache(max_weight=0.)

    impl_.new_cache(max_size=None)  # unbounded is fine


def test_lfu():
    c = impl_.new_cache()  # type: ignore
    for i in range(10):
        c[i] = i
        for _ in range(i):
            c[i]

    c = impl_.new_cache(max_size=5, eviction=impl_.LFU)
    for i in range(5):
        c[i] = i
    for _ in range(2):
        for i in range(5):
            if i != 2:
                c[i]
    c[2]
    c[6] = 6
