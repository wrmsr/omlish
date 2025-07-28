# @omlish-lite
# ruff: noqa: PT009 UP006 UP007
import sys
import threading
import time
import unittest

from ..testing import raise_in_thread


class TestRaiseInThread(unittest.TestCase):
    def test_raise_in_thread(self):
        if sys.implementation.name != 'cpython':
            self.skipTest('cpython only')

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
        self.assertTrue(t.is_alive())

        time.sleep(.4)
        self.assertFalse(f)

        raise_in_thread(t, FooError)

        t.join()
        self.assertFalse(t.is_alive())

        self.assertTrue(c > 1)
        self.assertIsInstance(e, FooError)
        self.assertTrue(f)
