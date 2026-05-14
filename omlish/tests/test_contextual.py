import typing as ta

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


# class MulIntShower(Shower[int]):
#     def __init__(self):


#


def test_shower():
    with cxl.bind({Shower[int]: IntShower()}):
        uses_int_shower(42)
        uses_int_shower_and_logs(42)

        calls_int_shower(42)
