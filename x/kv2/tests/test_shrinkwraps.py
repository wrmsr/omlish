import typing as ta

from ..bases import SizedQueryableKv
from ..interfaces import IterableKv
from ..interfaces import SizedKv
from ..shrinkwraps import ShrinkwrapFullKv
from ..shrinkwraps import shrinkwrap_factory


K = ta.TypeVar('K')
V = ta.TypeVar('V')


def test_shrinkwraps():
    class DummySizedQueryableKv(SizedQueryableKv[int, int]):
        def __getitem__(self, k: int, /) -> int:
            if k == 0:
                return 1
            raise KeyError(k)

        def __len__(self) -> int:
            return 1

    kv = DummySizedQueryableKv()
    assert kv[0] == 1
    assert len(kv) == 1

    if ta.TYPE_CHECKING:
        reveal_type(kv)  # noqa

    #

    def barf0(u: SizedQueryableKv[int, int]) -> None:
        pass

    barf0(kv)

    # def barf1(u: FullKv[int, int]) -> None:
    #     pass
    #
    # barf1(kv)

    #

    class Mul2Kv(ShrinkwrapFullKv[int, int]):
        def __getitem__(self, k: int, /) -> int:
            return self._u[k] * 2

        def items(self) -> ta.Iterator[tuple[int, int]]:
            return ((k, v * 2) for k, v in self._u.items())

    mul2 = shrinkwrap_factory(Mul2Kv)

    for _ in range(2):
        dw_kv = mul2(kv)
        assert dw_kv[0] == 2
        assert len(dw_kv) == 1
        assert isinstance(dw_kv, SizedKv)
        assert not isinstance(dw_kv, IterableKv)

        if ta.TYPE_CHECKING:
            reveal_type(dw_kv)  # noqa
