import typing as ta

from .bases import SortedIterableSizedQueryableKv
from .shrinkwraps import ShrinkwrapIterableKv
from .shrinkwraps import ShrinkwrapQueryableKv
from .shrinkwraps import ShrinkwrapSizedKv
from .shrinkwraps import ShrinkwrapSortedKv
from .shrinkwraps import shrinkwrap_factory_


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class UnmodifiableKv(
    ShrinkwrapSortedKv[K, V],
    ShrinkwrapIterableKv[K, V],
    ShrinkwrapSizedKv[K, V],
    ShrinkwrapQueryableKv[K, V],
):
    def __init__(
            self,
            u: SortedIterableSizedQueryableKv[K, V],
    ) -> None:
        super().__init__(u)

    _u: SortedIterableSizedQueryableKv[K, V]


unmodifiable = shrinkwrap_factory_(UnmodifiableKv)
