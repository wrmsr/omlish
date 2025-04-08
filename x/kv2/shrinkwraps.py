"""
TODO:
 - init_subclass should allow piecewise method defs as long as no kv interface is partially implemented. default impls
   are optional and only apply to the non-2, KA=KB/VA=VB case.
"""
import functools
import typing as ta

from omlish import check
from omlish import lang

from .bases import KV_BASES_BY_MRO
from .bases import FullKv
from .bases import KvToKvFunc
from .interfaces import KV_INTERFACE_MEMBERS
from .interfaces import KV_INTERFACES
from .interfaces import IterableKv
from .interfaces import Kv
from .interfaces import KvMro
from .interfaces import MutableKv
from .interfaces import QueryableKv
from .interfaces import SizedKv
from .interfaces import check_kv_interface_mro
from .interfaces import get_cls_kv_interface_mro
from .wrappers import WrapperKv


K = ta.TypeVar('K')
V = ta.TypeVar('V')

# 'Above' the wrapper
KA = ta.TypeVar('KA')
VA = ta.TypeVar('VA')

# 'Below' the wrapper
KB = ta.TypeVar('KB')
VB = ta.TypeVar('VB')

# P = ta.ParamSpec('P')


##


class _BoundShrinkwrapKv:
    pass


class ShrinkwrapKv2(WrapperKv[KA, VA], ta.Generic[KA, VA, KB, VB]):
    def __init__(self, u: Kv[KB, VB]) -> None:
        super().__init__()

        self._u = u

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if issubclass(cls, _BoundShrinkwrapKv):
            if _BoundShrinkwrapKv not in cls.__bases__:
                raise TypeError(f'Must not subclass dynamic wrapper kvs: {cls}')
            return

        for i_cls in KV_INTERFACES:
            if issubclass(cls, i_cls):
                raise TypeError(f'ShrinkwrapKv subclass {cls} should not directly implement interface {i_cls}')

        try:
            interfaces_by_shrinkwrap = INTERFACES_BY_SHRINKWRAP
        except NameError:
            # Module initializing
            return

        sw_mro = tuple(wc for wc in cls.__bases__ if wc in interfaces_by_shrinkwrap)
        sorted_sw_mro = tuple(sorted(sw_mro, key=lambda wc: KV_INTERFACES.index(interfaces_by_shrinkwrap[wc])))
        if sw_mro != sorted_sw_mro:
            raise TypeError(
                f'ShrinkwrapKv subclass {cls} must keep wrapper subclasses in proper order: '
                f'got {sw_mro}, '
                f'expected {sorted_sw_mro}',
            )

    @ta.final
    def underlying(self) -> ta.Iterable[Kv[KB, VB]]:
        return [self._u]


ShrinkwrapKv: ta.TypeAlias = ShrinkwrapKv2[K, V, K, V]


##


class ShrinkwrapQueryableKv(ShrinkwrapKv[K, V], lang.Abstract):
    _u: QueryableKv[K, V]

    def __getitem__(self, k: K, /) -> V:
        return self._u[k]


class ShrinkwrapSizedKv(ShrinkwrapKv[K, V], lang.Abstract):
    _u: SizedKv[K, V]

    def __len__(self) -> int:
        return len(self._u)


class ShrinkwrapIterableKv(ShrinkwrapKv[K, V], lang.Abstract):
    _u: IterableKv[K, V]

    def items(self) -> ta.Iterator[tuple[K, V]]:
        return self._u.items()


class ShrinkwrapMutableKv(ShrinkwrapKv[K, V], lang.Abstract):
    _u: MutableKv[K, V]

    def __setitem__(self, k: K, v: V, /) -> None:
        self._u[k] = v

    def __delitem__(self, k: K, /) -> None:
        del self._u[k]


##


SHRINKWRAPS_BY_INTERFACE: ta.Mapping[type[Kv], type[ShrinkwrapKv]] = {
    MutableKv: ShrinkwrapMutableKv,
    IterableKv: ShrinkwrapIterableKv,
    SizedKv: ShrinkwrapSizedKv,
    QueryableKv: ShrinkwrapQueryableKv,
}

INTERFACES_BY_SHRINKWRAP: ta.Mapping[type[ShrinkwrapKv], type[Kv]] = {
    wc: ic
    for ic, wc in SHRINKWRAPS_BY_INTERFACE.items()
}


##


class ShrinkwrapFullKv(
    ShrinkwrapMutableKv[K, V],
    ShrinkwrapIterableKv[K, V],
    ShrinkwrapSizedKv[K, V],
    ShrinkwrapQueryableKv[K, V],
    lang.Abstract,
):
    _u: FullKv[K, V]


##


class ShrinkwrapNotImplementedError(TypeError):
    pass


def _raise_shrinkwrap_not_implemented_error(self, *args) -> ta.NoReturn:
    raise ShrinkwrapNotImplementedError


_BOUND_SHRINKWRAP_CACHE_ATTR = '__shrinkwrap_kv_bound_cache__'


def bind_shrinkwrap_cls(w_cls: type[ShrinkwrapKv2], iface_mro: KvMro) -> type[Kv]:
    check.issubclass(w_cls, ShrinkwrapKv2)
    check_kv_interface_mro(iface_mro)

    kv_base_cls = KV_BASES_BY_MRO[iface_mro]

    cache: dict[KvMro, type[Kv]]
    try:
        cache = w_cls.__dict__[_BOUND_SHRINKWRAP_CACHE_ATTR]
    except KeyError:
        cache = {}
        setattr(w_cls, _BOUND_SHRINKWRAP_CACHE_ATTR, cache)

    bw_cls: type[Kv]
    try:
        bw_cls = cache[iface_mro]
    except KeyError:
        pass
    else:
        check.issubclass(bw_cls, w_cls)
        check.issubclass(bw_cls, kv_base_cls)
        return bw_cls

    ns = {}
    for i_cls, i_mbr_lst in KV_INTERFACE_MEMBERS.items():
        m_cls = SHRINKWRAPS_BY_INTERFACE[i_cls]

        if i_cls not in iface_mro:
            if issubclass(w_cls, m_cls):
                for a in i_mbr_lst:
                    ns[a] = _raise_shrinkwrap_not_implemented_error

            continue

    # FIXME: still ta.Generic[K, V] - propagate down properly
    base_cls_lst = [
        _BoundShrinkwrapKv,
        w_cls,
        kv_base_cls,
        lang.Final,
    ]

    bw_cls = ta.cast(type[Kv], lang.new_type(
        f'{w_cls.__name__}${kv_base_cls.__name__}',
        tuple(base_cls_lst),
        ns,
    ))

    cache[iface_mro] = bw_cls

    return bw_cls


def shrinkwrap_factory_(w_cls):
    w_cls = check.issubclass(w_cls, ShrinkwrapKv2)

    @functools.wraps(w_cls)
    def inner(kv, *args, **kwargs):
        bw_cls = bind_shrinkwrap_cls(w_cls, get_cls_kv_interface_mro(type(kv)))
        return bw_cls(kv, *args, **kwargs)  # type: ignore[call-arg]

    return ta.cast(KvToKvFunc, inner)


# def shrinkwrap_factory(w_cls: ta.Callable[P, ShrinkwrapKv[K, V]]) -> KvToKvFunc[P, K, V]:
def shrinkwrap_factory(w_cls: type[ShrinkwrapKv[K, V]]) -> KvToKvFunc[K, V, K, V]:
    return shrinkwrap_factory_(w_cls)
