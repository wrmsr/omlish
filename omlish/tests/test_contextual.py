import dataclasses as dc
import typing as ta

import pytest

from .. import contextual as cxl
from ..logs import all as logs


T = ta.TypeVar('T')


log = logs.get_module_logger(globals())


##


class Shower(ta.Generic[T]):
    def show(self, v: T) -> None:
        raise NotImplementedError


class IntShower(Shower[int]):
    def show(self, v: int) -> None:
        print(f'int({v})')


#


@cxl.wrap()
def uses_int_shower(
        i: int,
        *,
        int_shower: Shower[int] = cxl.param(),
) -> None:
    int_shower.show(i)


#


@cxl.wrap()
def uses_int_shower_and_logs(
        i: int,
        *,
        int_shower: Shower[int] = cxl.param(),
        log: logs.Logger = cxl.param(log),  # noqa
) -> None:
    log.info(lambda: f'showing {i}')
    int_shower.show(i)


#


def calls_int_shower(i: int) -> None:
    uses_int_shower(i)


#


class MulIntShower(Shower[int]):
    @cxl.wrap()
    def __init__(
            self,
            n: int,
            *,
            wrapped: Shower[int] = cxl.param(),
    ) -> None:
        self._n = n
        self._wrapped = wrapped

    def show(self, v: int) -> None:
        self._wrapped.show(v * self._n)


#


@cxl.wrap()
@dc.dataclass(frozen=True)
class DcIncIntShower(Shower[int]):
    wrapped: Shower[int] = cxl.param()

    def show(self, v: int) -> None:
        self.wrapped.show(v + 1)


#


class Frobber:
    def frob(self) -> None:
        print('frob')


@cxl.wrap()
def int_shower_with_frobber(
        *,
        int_shower: Shower[int] = cxl.param(),
        frobber: Frobber | None = cxl.param(None),
) -> None:
    if frobber is not None:
        frobber.frob()
    int_shower.show(42)


#


def test_shower():
    with pytest.raises(cxl.UnboundError):
        uses_int_shower(42)

    with cxl.bind({Shower[int]: IntShower()}):
        uses_int_shower(42)
        uses_int_shower_and_logs(42)

        calls_int_shower(42)

        with cxl.bind({Shower[int]: MulIntShower(2)}):
            calls_int_shower(42)

            with cxl.bind({Shower[int]: DcIncIntShower()}):
                calls_int_shower(42)

        int_shower_with_frobber()

        with cxl.bind({Frobber: Frobber()}):
            int_shower_with_frobber()
