# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import typing as ta
import unittest

from ...logs.base import Logger
from ...logs.modules import get_module_logger
from ..contextual import UnboundContextualError
from ..contextual import _UnboundContextualParam
from ..contextual import contextual_bind
from ..contextual import contextual_param
from ..contextual import contextual_wrap


T = ta.TypeVar('T')


log = get_module_logger(globals())


##


class Shower(ta.Generic[T]):
    def show(self, v: T) -> None:
        raise NotImplementedError


class IntShower(Shower[int]):
    def show(self, v: int) -> None:
        print(f'int({v})')


#


@contextual_wrap()
def uses_int_shower(
        i: int,
        *,
        int_shower: Shower[int] = contextual_param(),
) -> None:
    int_shower.show(i)


#


@contextual_wrap()
def uses_int_shower_and_logs(
        i: int,
        *,
        int_shower: Shower[int] = contextual_param(),
        log: Logger = contextual_param(log),  # noqa
) -> None:
    log.info(lambda: f'showing {i}')
    int_shower.show(i)


#


def calls_int_shower(i: int) -> None:
    uses_int_shower(i)


#


class MulIntShower(Shower[int]):
    @contextual_wrap()
    def __init__(
            self,
            n: int,
            *,
            wrapped: Shower[int] = contextual_param(),
    ) -> None:
        self._n = n
        self._wrapped = wrapped

    def show(self, v: int) -> None:
        self._wrapped.show(v * self._n)


#


@contextual_wrap()
@dc.dataclass(frozen=True)
class DcIncIntShower(Shower[int]):
    wrapped: Shower[int] = contextual_param()

    def show(self, v: int) -> None:
        self.wrapped.show(v + 1)


#


class Frobber:
    def frob(self) -> None:
        print('frob')


@contextual_wrap()
def int_shower_with_frobber(
        *,
        int_shower: Shower[int] = contextual_param(),
        frobber: ta.Optional[Frobber] = contextual_param(None),
) -> None:
    if frobber is not None:
        frobber.frob()
    int_shower.show(42)


#


class TestContextual(unittest.TestCase):
    def test_unbound_thingy(self):
        with self.assertRaises(UnboundContextualError):
            _UnboundContextualParam()()

    def test_shower(self):
        with self.assertRaises(UnboundContextualError):
            uses_int_shower(42)

        with contextual_bind({Shower[int]: IntShower()}):
            uses_int_shower(42)
            uses_int_shower_and_logs(42)

            calls_int_shower(42)

            with contextual_bind({Shower[int]: MulIntShower(2)}):
                calls_int_shower(42)

                with contextual_bind({Shower[int]: DcIncIntShower()}):
                    calls_int_shower(42)

            int_shower_with_frobber()

            with contextual_bind({Frobber: Frobber()}):
                int_shower_with_frobber()
