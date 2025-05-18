# @omlish-generated
"""
Note: This is all just a hacky workaround for python's lack of intersection types. See:

  https://github.com/python/typing/issues/213

"""
import typing as ta

from omlish import lang

from .interfaces import IterableKv
from .interfaces import Kv
from .interfaces import MutableKv
from .interfaces import QueryableKv
from .interfaces import SizedKv
from .interfaces import SortedKv


K = ta.TypeVar('K')
V = ta.TypeVar('V')

KF = ta.TypeVar('KF')
VF = ta.TypeVar('VF')

KT = ta.TypeVar('KT')
VT = ta.TypeVar('VT')


##


if __name__ == '__main__':
    raise RuntimeError('Must not be run as __main__ - would produce duplicate kv base classes.')


##


__all__ = [  # noqa
    'SizedQueryableKv',
    'IterableQueryableKv',
    'IterableSizedKv',
    'SortedQueryableKv',
    'SortedSizedKv',
    'SortedIterableKv',
    'MutableQueryableKv',
    'MutableSizedKv',
    'MutableIterableKv',
    'MutableSortedKv',
    'IterableSizedQueryableKv',
    'SortedSizedQueryableKv',
    'SortedIterableQueryableKv',
    'SortedIterableSizedKv',
    'MutableSizedQueryableKv',
    'MutableIterableQueryableKv',
    'MutableIterableSizedKv',
    'MutableSortedQueryableKv',
    'MutableSortedSizedKv',
    'MutableSortedIterableKv',
    'SortedIterableSizedQueryableKv',
    'MutableIterableSizedQueryableKv',
    'MutableSortedSizedQueryableKv',
    'MutableSortedIterableQueryableKv',
    'MutableSortedIterableSizedKv',
    'MutableSortedIterableSizedQueryableKv',
    'FullKv',

    'KV_BASES_BY_MRO',

    'KvToKvFunc2',
    'KvToKvFunc',
]


##


class SizedQueryableKv(  # noqa
    SizedKv[K, V],
    QueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class IterableQueryableKv(  # noqa
    IterableKv[K, V],
    QueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class IterableSizedKv(  # noqa
    IterableKv[K, V],
    SizedKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class SortedQueryableKv(  # noqa
    SortedKv[K, V],
    QueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class SortedSizedKv(  # noqa
    SortedKv[K, V],
    SizedKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class SortedIterableKv(  # noqa
    SortedKv[K, V],
    IterableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableQueryableKv(  # noqa
    MutableKv[K, V],
    QueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSizedKv(  # noqa
    MutableKv[K, V],
    SizedKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableIterableKv(  # noqa
    MutableKv[K, V],
    IterableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSortedKv(  # noqa
    MutableKv[K, V],
    SortedKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class IterableSizedQueryableKv(  # noqa
    IterableSizedKv[K, V],
    IterableQueryableKv[K, V],
    SizedQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class SortedSizedQueryableKv(  # noqa
    SortedSizedKv[K, V],
    SortedQueryableKv[K, V],
    SizedQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class SortedIterableQueryableKv(  # noqa
    SortedIterableKv[K, V],
    SortedQueryableKv[K, V],
    IterableQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class SortedIterableSizedKv(  # noqa
    SortedIterableKv[K, V],
    SortedSizedKv[K, V],
    IterableSizedKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSizedQueryableKv(  # noqa
    MutableSizedKv[K, V],
    MutableQueryableKv[K, V],
    SizedQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableIterableQueryableKv(  # noqa
    MutableIterableKv[K, V],
    MutableQueryableKv[K, V],
    IterableQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableIterableSizedKv(  # noqa
    MutableIterableKv[K, V],
    MutableSizedKv[K, V],
    IterableSizedKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSortedQueryableKv(  # noqa
    MutableSortedKv[K, V],
    MutableQueryableKv[K, V],
    SortedQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSortedSizedKv(  # noqa
    MutableSortedKv[K, V],
    MutableSizedKv[K, V],
    SortedSizedKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSortedIterableKv(  # noqa
    MutableSortedKv[K, V],
    MutableIterableKv[K, V],
    SortedIterableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class SortedIterableSizedQueryableKv(  # noqa
    SortedIterableSizedKv[K, V],
    SortedIterableQueryableKv[K, V],
    SortedSizedQueryableKv[K, V],
    IterableSizedQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableIterableSizedQueryableKv(  # noqa
    MutableIterableSizedKv[K, V],
    MutableIterableQueryableKv[K, V],
    MutableSizedQueryableKv[K, V],
    IterableSizedQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSortedSizedQueryableKv(  # noqa
    MutableSortedSizedKv[K, V],
    MutableSortedQueryableKv[K, V],
    MutableSizedQueryableKv[K, V],
    SortedSizedQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSortedIterableQueryableKv(  # noqa
    MutableSortedIterableKv[K, V],
    MutableSortedQueryableKv[K, V],
    MutableIterableQueryableKv[K, V],
    SortedIterableQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSortedIterableSizedKv(  # noqa
    MutableSortedIterableKv[K, V],
    MutableSortedSizedKv[K, V],
    MutableIterableSizedKv[K, V],
    SortedIterableSizedKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


class MutableSortedIterableSizedQueryableKv(  # noqa
    MutableSortedIterableSizedKv[K, V],
    MutableSortedIterableQueryableKv[K, V],
    MutableSortedSizedQueryableKv[K, V],
    MutableIterableSizedQueryableKv[K, V],
    SortedIterableSizedQueryableKv[K, V],
    Kv[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


FullKv: ta.TypeAlias = MutableSortedIterableSizedQueryableKv[K, V]


##


KV_BASES_BY_MRO: ta.Mapping[tuple[type[Kv], ...], type[Kv]] = {
    (QueryableKv,): QueryableKv,
    (SizedKv,): SizedKv,
    (IterableKv,): IterableKv,
    (SortedKv,): SortedKv,
    (MutableKv,): MutableKv,
    (SizedKv, QueryableKv): SizedQueryableKv,
    (IterableKv, QueryableKv): IterableQueryableKv,
    (IterableKv, SizedKv): IterableSizedKv,
    (SortedKv, QueryableKv): SortedQueryableKv,
    (SortedKv, SizedKv): SortedSizedKv,
    (SortedKv, IterableKv): SortedIterableKv,
    (MutableKv, QueryableKv): MutableQueryableKv,
    (MutableKv, SizedKv): MutableSizedKv,
    (MutableKv, IterableKv): MutableIterableKv,
    (MutableKv, SortedKv): MutableSortedKv,
    (IterableKv, SizedKv, QueryableKv): IterableSizedQueryableKv,
    (SortedKv, SizedKv, QueryableKv): SortedSizedQueryableKv,
    (SortedKv, IterableKv, QueryableKv): SortedIterableQueryableKv,
    (SortedKv, IterableKv, SizedKv): SortedIterableSizedKv,
    (MutableKv, SizedKv, QueryableKv): MutableSizedQueryableKv,
    (MutableKv, IterableKv, QueryableKv): MutableIterableQueryableKv,
    (MutableKv, IterableKv, SizedKv): MutableIterableSizedKv,
    (MutableKv, SortedKv, QueryableKv): MutableSortedQueryableKv,
    (MutableKv, SortedKv, SizedKv): MutableSortedSizedKv,
    (MutableKv, SortedKv, IterableKv): MutableSortedIterableKv,
    (SortedKv, IterableKv, SizedKv, QueryableKv): SortedIterableSizedQueryableKv,
    (MutableKv, IterableKv, SizedKv, QueryableKv): MutableIterableSizedQueryableKv,
    (MutableKv, SortedKv, SizedKv, QueryableKv): MutableSortedSizedQueryableKv,
    (MutableKv, SortedKv, IterableKv, QueryableKv): MutableSortedIterableQueryableKv,
    (MutableKv, SortedKv, IterableKv, SizedKv): MutableSortedIterableSizedKv,
    (MutableKv, SortedKv, IterableKv, SizedKv, QueryableKv): MutableSortedIterableSizedQueryableKv,
}


##


class KvToKvFunc2(ta.Protocol[KF, VF, KT, VT]):
    @ta.overload
    def __call__(
        self,
        kv: MutableSortedIterableSizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSortedIterableSizedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSortedIterableSizedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSortedIterableSizedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSortedIterableQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSortedIterableQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSortedSizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSortedSizedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableIterableSizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableIterableSizedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SortedIterableSizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SortedIterableSizedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSortedIterableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSortedIterableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSortedSizedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSortedSizedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSortedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSortedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableIterableSizedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableIterableSizedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableIterableQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableIterableQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSizedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SortedIterableSizedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SortedIterableSizedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SortedIterableQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SortedIterableQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SortedSizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SortedSizedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: IterableSizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableSizedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSortedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSortedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableIterableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableIterableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSizedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSizedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SortedIterableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SortedIterableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SortedSizedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SortedSizedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SortedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SortedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: IterableSizedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableSizedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: IterableQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SizedQueryableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SortedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SortedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: IterableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: SizedKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SizedKv[KT, VT]: ...

    @ta.overload
    def __call__(
        self,
        kv: QueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> QueryableKv[KT, VT]: ...

    def __call__(self, kv, *args, **kwargs): ...


KvToKvFunc: ta.TypeAlias = KvToKvFunc2[K, V, K, V]


##


from . import interfaces as _interfaces  # noqa

_interfaces._KV_BASES_BY_MRO = KV_BASES_BY_MRO  # noqa
