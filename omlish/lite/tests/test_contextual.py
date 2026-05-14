# @omlish-lite
import typing as ta
import unittest

from ..contextual import contextual_bind
from ..contextual import contextual_param
from ..contextual import contextual_wrap


T = ta.TypeVar('T')


##


class TestContextual(unittest.TestCase):
    def test_shower(self):
        class Shower(ta.Generic[T]):
            def show(self, v: T) -> None:
                raise NotImplementedError

        class IntShower(Shower[int]):
            def show(self, v: int) -> None:
                print(f'int({v})')

        @contextual_wrap()
        def uses_int_shower(
                i: int,
                *,
                int_shower: Shower[int] = contextual_param(),
        ) -> None:
            int_shower.show(i)

        with contextual_bind({Shower[int]: IntShower()}):
            uses_int_shower(42)
