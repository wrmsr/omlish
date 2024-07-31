import sys
import threading
import time

import pytest

from ..testing import raise_in_thread


@pytest.mark.skipif(sys.implementation.name != 'cpython', reason='cpython only')
def test_raise_in_thread():
    c = 0
    e = None
    f = False

    class FooError(Exception):
        pass

    def proc():
        nonlocal c
        nonlocal e
        nonlocal f
        try:
            while True:
                time.sleep(.05)
                c += 1
        except FooError as e_:
            e = e_
        finally:
            f = True

    t = threading.Thread(target=proc)

    t.start()
    assert t.is_alive()

    time.sleep(.4)
    assert not f

    raise_in_thread(t, FooError)

    t.join()
    assert not t.is_alive()

    assert c > 1
    assert isinstance(e, FooError)
    assert f
