import typing as ta

from .bases import IterableSizedQueryableKv
from .shrinkwraps import ShrinkwrapIterableKv
from .shrinkwraps import ShrinkwrapQueryableKv
from .shrinkwraps import ShrinkwrapSizedKv
from .shrinkwraps import shrinkwrap_factory_


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class UnmodifiableKv(
    ShrinkwrapIterableKv[K, V],
    ShrinkwrapSizedKv[K, V],
    ShrinkwrapQueryableKv[K, V],
):
    def __init__(
            self,
            u: IterableSizedQueryableKv[K, V],
    ) -> None:
        super().__init__(u)

    _u: IterableSizedQueryableKv[K, V]


unmodifiable = shrinkwrap_factory_(UnmodifiableKv)
