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
    'MutableQueryableKv',
    'MutableSizedKv',
    'MutableIterableKv',
    'IterableSizedQueryableKv',
    'MutableSizedQueryableKv',
    'MutableIterableQueryableKv',
    'MutableIterableSizedKv',
    'MutableIterableSizedQueryableKv',
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


class IterableSizedQueryableKv(  # noqa
    IterableSizedKv[K, V],
    IterableQueryableKv[K, V],
    SizedQueryableKv[K, V],
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


FullKv: ta.TypeAlias = MutableIterableSizedQueryableKv[K, V]


##


KV_BASES_BY_MRO: ta.Mapping[tuple[type[Kv], ...], type[Kv]] = {
    (QueryableKv,): QueryableKv,
    (SizedKv,): SizedKv,
    (IterableKv,): IterableKv,
    (MutableKv,): MutableKv,
    (SizedKv, QueryableKv): SizedQueryableKv,
    (IterableKv, QueryableKv): IterableQueryableKv,
    (IterableKv, SizedKv): IterableSizedKv,
    (MutableKv, QueryableKv): MutableQueryableKv,
    (MutableKv, SizedKv): MutableSizedKv,
    (MutableKv, IterableKv): MutableIterableKv,
    (IterableKv, SizedKv, QueryableKv): IterableSizedQueryableKv,
    (MutableKv, SizedKv, QueryableKv): MutableSizedQueryableKv,
    (MutableKv, IterableKv, QueryableKv): MutableIterableQueryableKv,
    (MutableKv, IterableKv, SizedKv): MutableIterableSizedKv,
    (MutableKv, IterableKv, SizedKv, QueryableKv): MutableIterableSizedQueryableKv,
}


##


class KvToKvFunc2(ta.Protocol[KF, VF, KT, VT]):
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
        kv: IterableSizedQueryableKv[KF, VF],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableSizedQueryableKv[KT, VT]: ...

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
