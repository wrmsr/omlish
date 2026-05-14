import typing as ta

from .. import contextual as cxl


T = ta.TypeVar('T')


##


def test_shower():
    class Shower(ta.Generic[T]):
        def show(self, v: T) -> None:
            raise NotImplementedError

    class IntShower(Shower[int]):
        def show(self, v: int) -> None:
            print(f'int({v})')

    @cxl.wrap()
    def uses_int_shower(
            i: int,
            *,
            int_shower: Shower[int] = cxl.param(),
    ) -> None:
        int_shower.show(i)

    with cxl.bind({Shower[int]: IntShower()}):
        uses_int_shower(42)
