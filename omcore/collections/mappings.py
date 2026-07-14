import abc
import collections.abc
import operator
import typing as ta
import weakref

from .. import lang


with lang.auto_proxy_import(globals()):
    from . import identity as _identity


K = ta.TypeVar('K')
V = ta.TypeVar('V')

K_co = ta.TypeVar('K_co', covariant=True)
V_co = ta.TypeVar('V_co', covariant=True)


##


def multikey_dict(dct: ta.Mapping[ta.Iterable[K] | K, V], *, deep: bool = False) -> dict[K, V]:
    ret = {}
    for k, v in dct.items():
        if deep and isinstance(v, dict):
            v = multikey_dict(v, deep=True)  # type: ignore
        if isinstance(k, tuple):
            for sk in k:
                ret[sk] = v
        else:
            ret[k] = v
    return ret


##


def guarded_map_update(
        dst: ta.MutableMapping[ta.Any, ta.Any],
        *srcs: ta.Mapping[ta.Any, ta.Any],
) -> ta.MutableMapping[ta.Any, ta.Any]:
    for src in srcs:
        for k, v in src.items():
            if k in dst:
                raise KeyError(k)
            dst[k] = v
    return dst


##


def map_contains(m: ta.Mapping, k: ta.Any) -> bool:
    try:
        m[k]
    except KeyError:
        return False
    else:
        return True


##


class MissingDict(dict[K, V]):
    def __init__(self, missing_fn: ta.Callable[[K], V]) -> None:
        if not callable(missing_fn):
            raise TypeError(missing_fn)

        super().__init__()

        self._missing_fn = missing_fn

    def __missing__(self, key):
        v = self[key] = self._missing_fn(key)
        return v


##


def dict_factory[K, V](
        *,
        identity: bool = False,
        weak: bool = False,
) -> ta.Callable[..., ta.MutableMapping[K, V]]:
    if identity:
        if weak:
            return _identity.IdentityWeakKeyDictionary
        else:
            return _identity.IdentityKeyDict
    elif weak:
        return weakref.WeakKeyDictionary
    else:
        return dict


##


@ta.final
class IterValuesView(collections.abc.ValuesView[V]):
    _mapping: IterValuesViewMapping[ta.Any, V]

    def __iter__(self) -> ta.Iterator[V]:
        return self._mapping.itervalues()  # noqa


class IterValuesViewMapping(collections.abc.Mapping[K, V]):
    @ta.final
    def values(self) -> IterValuesView[V]:
        return IterValuesView(self)

    @abc.abstractmethod
    def itervalues(self) -> ta.Iterator[V]:
        raise NotImplementedError


#


@ta.final
class IterItemsView(collections.abc.ItemsView[K, V]):
    _mapping: IterItemsViewMapping[K, V]

    def __iter__(self) -> ta.Iterator[tuple[K, V]]:
        return self._mapping.iteritems()  # noqa


class IterItemsViewMapping(collections.abc.Mapping[K, V]):
    @ta.final
    def items(self) -> IterItemsView[K, V]:
        return IterItemsView(self)

    @abc.abstractmethod
    def iteritems(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError


#


class HasIterItems(ta.Protocol[K_co, V_co]):
    def iteritems(self) -> ta.Iterator[tuple[K_co, V_co]]: ...


def iteritems_itervalues(ii: HasIterItems[K, V]) -> ta.Iterator[V]:
    return map(operator.itemgetter(1), ii.iteritems())
