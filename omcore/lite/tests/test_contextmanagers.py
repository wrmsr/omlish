# ruff: noqa: PT009 PT027
import unittest

from ..contextmanagers import ExitStacked


class CmTracker:
    entered = False
    exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exited = True


class TestExitStacked(unittest.TestCase):
    def test_exit(self):
        class Foo(ExitStacked):
            def __init__(self):
                super().__init__()
                self.t = CmTracker()

            def _enter_contexts(self):
                self._enter_context(self.t)
                raise RuntimeError('barf')

        foo = Foo()
        with self.assertRaises(RuntimeError):  # noqa
            with foo:
                pass

        self.assertTrue(foo.t.entered)
        self.assertTrue(foo.t.exited)
