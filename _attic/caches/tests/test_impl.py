import gc
import weakref

import pytest

from .. import impl as impl_


def test_cache():
    c = impl_.new_cache(max_size=2)
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
    c = impl_.new_cache(weak_keys=True)
    c[k] = 1
    assert c[k] == 1
    assert len(c) == 1
    kref = weakref.ref(K)  # noqa
    del k
    gc.collect()
    assert len(c) == 0


def test_weak_values():
    class V:
        pass
    c = impl_.new_cache(weak_values=True)
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
    c = impl_.new_cache(expire_after_write=2, clock=lambda: clock)
    c[0] = 'a'
    c[1] = 'b'
    clock = 1
    assert c[0] == 'a'
    clock = 3
    with pytest.raises(KeyError):
        c.__getitem__(0)


def test_lfu():
    c = impl_.new_cache()
    for i in range(10):
        c[i] = i
        for j in range(i):
            c[i]

    c = impl_.new_cache(max_size=5, eviction=impl_.CacheImpl.LFU)
    for i in range(5):
        c[i] = i
    for _ in range(2):
        for i in range(5):
            if i != 2:
                c[i]
    c[2]
    c[6] = 6
