# ruff: noqa: PT009 PT027 UP037
import typing as ta  # noqa
import unittest

from ..injectinspect import _do_injection_inspect  # noqa


T = ta.TypeVar('T')


class TestInspect(unittest.TestCase):
    def test_overridden_new(self):
        # See note in _do_injection_inspect about failing on 3.8.

        class NonGenericNullary:
            pass

        class GenericNullary(ta.Generic[T]):
            pass

        cls: ta.Any
        for cls in [NonGenericNullary, GenericNullary]:
            insp = _do_injection_inspect(cls)

            self.assertEqual(len(insp.signature.parameters) - insp.args_offset, 0)

        class NonGenericFoo:
            def __init__(self, t: T) -> None:
                pass

        class GenericFoo(ta.Generic[T]):
            def __init__(self, t: T) -> None:
                pass

        for cls in [NonGenericFoo, GenericFoo]:
            insp = _do_injection_inspect(cls)

            self.assertEqual(len(insp.signature.parameters) - insp.args_offset, 1)
            self.assertIs(insp.signature.parameters['t'].annotation, T)
