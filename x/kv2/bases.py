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


class KvToKvFunc(ta.Protocol[K, V]):
    @ta.overload
    def __call__(
        self,
        kv: MutableIterableSizedQueryableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableIterableSizedQueryableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableIterableSizedKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableIterableSizedKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableIterableQueryableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableIterableQueryableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSizedQueryableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSizedQueryableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: IterableSizedQueryableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableSizedQueryableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableIterableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableIterableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableSizedKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableSizedKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableQueryableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableQueryableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: IterableSizedKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableSizedKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: IterableQueryableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableQueryableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: SizedQueryableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SizedQueryableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: MutableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> MutableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: IterableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> IterableKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: SizedKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> SizedKv[K, V]: ...

    @ta.overload
    def __call__(
        self,
        kv: QueryableKv[K, V],
        *args: ta.Any,
        **kwargs: ta.Any,
    ) -> QueryableKv[K, V]: ...

    def __call__(self, kv, *args, **kwargs): ...


##


from . import interfaces as _interfaces  # noqa

_interfaces._KV_BASES_BY_MRO = KV_BASES_BY_MRO  # noqa
