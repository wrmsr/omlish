"""
TODO:
 - lock?
"""
import dataclasses as dc
import typing as ta
import weakref

from .. import check
from .. import lang
from .mappings import dict_factory


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class AttrRegistry(ta.Generic[K, V]):
    """
    MRO-honoring class member registry. There are many ways to do this, and this one is attr name based: a class is
    considered to have objects registered to it based on whether or not they are accessible by a non-shadowed,
    MRO-resolved named attribute on that class.

    Care must be taken when overriding registered objects from superclasses in subclasses - shadowing the attribute name
    of the superclass member will not automatically register the new member with the same name to the registry - it must
    be explicitly registered itself. This is a feature, allowing for selective de-registration of objects in subclasses
    via name shadowing.
    """

    def __init__(
            self,
            *,
            requires_override: bool = False,
            is_override: ta.Callable[[ta.Any], bool] | None = None,
            forbid_duplicates: bool = False,
            identity: bool = False,
            weak: bool = False,
    ) -> None:
        super().__init__()

        self._requires_override = requires_override
        self._is_override = is_override
        self._forbid_duplicates = forbid_duplicates
        self._identity = identity
        self._weak = weak

        self._objs: ta.MutableMapping[K, V] = dict_factory(identity=identity, weak=weak)()
        self._invalidate_callbacks: list[ta.Callable[[], None]] = []

    def add_invalidate_callback(self, callback: ta.Callable[[], None]) -> None:
        self._invalidate_callbacks.append(callback)

    @ta.overload
    def register(self, obj: K, val: V) -> None:
        ...

    @ta.overload
    def register(self, val: V) -> ta.Callable[[T], T]:
        ...

    def register(self, *args):
        def inner(obj, val):
            check.not_in(obj, self._objs)

            self._objs[obj] = val

            for iv in self._invalidate_callbacks:
                iv()

            return obj

        if len(args) == 1:
            return lambda obj: inner(obj, args[0])
        elif len(args) == 2:
            inner = inner(*args)
            return None
        else:
            raise TypeError(args)

    def _lookup(self, obj: ta.Any) -> lang.Maybe[V]:
        if not self._identity:
            try:
                hash(obj)
            except TypeError:
                return lang.empty()

        try:
            val = self._objs[obj]
        except KeyError:
            return lang.empty()
        else:
            return lang.just(val)

    @dc.dataclass()
    class DuplicatesForbiddenError(Exception):
        owner_cls: type
        instance_cls: type
        att: str
        ex_att: str

    def collect(self, instance_cls: type, owner_cls: type | None = None) -> dict[str, tuple[K, V]]:
        if owner_cls is None:
            owner_cls = instance_cls

        mro = instance_cls.__mro__[-2::-1]
        try:
            mro_pos = mro.index(owner_cls)
        except ValueError:
            raise TypeError(f'Owner class {owner_cls} not in mro of instance class {instance_cls}') from None

        mro_dct: dict[str, list[tuple[type, ta.Any]]] = {}
        for cur_cls in mro[:mro_pos + 1]:
            for att, obj in cur_cls.__dict__.items():
                if att not in mro_dct:
                    if not self._lookup(obj).present:
                        continue

                try:
                    lst = mro_dct[att]
                except KeyError:
                    lst = mro_dct[att] = []
                lst.append((cur_cls, obj))

        #

        seen: ta.MutableMapping[ta.Any, str] | None = None
        if self._forbid_duplicates:
            seen = dict_factory(identity=self._identity)()

        out: dict[str, tuple[K, V]] = {}
        for att, lst in mro_dct.items():
            if not lst:
                raise RuntimeError
            _, obj = lst[-1]

            if len(lst) > 1:
                if self._requires_override and not (self._is_override or lang.is_override)(obj):
                    raise lang.RequiresOverrideError(
                        att,
                        instance_cls,
                        lst[-1][0],
                        lst[0][0],
                    )

            if not (mv := self._lookup(obj)).present:
                continue

            if seen is not None:
                try:
                    ex_att = seen[obj]
                except KeyError:
                    pass
                else:
                    raise AttrRegistry.DuplicatesForbiddenError(owner_cls, instance_cls, att, ex_att)  # noqa
                seen[obj] = att

            out[att] = (obj, mv.must())

        return out


##


class AttrRegistryCache(ta.Generic[K, V, T]):
    def __init__(
            self,
            registry: AttrRegistry[K, V],
            prepare: ta.Callable[[type, dict[str, tuple[K, V]]], T],
    ) -> None:
        super().__init__()

        self._registry = registry
        self._prepare = prepare

        self._cache: dict[ta.Any, T] = {}

        def cache_remove(k, self_ref=weakref.ref(self)):
            if (ref_self := self_ref()) is not None:
                cache = ref_self._cache  # noqa
                try:
                    del cache[k]
                except KeyError:
                    pass

        self._cache_remove = cache_remove

        registry.add_invalidate_callback(self._cache.clear)

    def get(self, instance_cls: type) -> T:
        cls_ref = weakref.ref(instance_cls)
        try:
            return self._cache[cls_ref]
        except KeyError:
            pass
        del cls_ref

        collected = self._registry.collect(instance_cls)
        out = self._prepare(instance_cls, collected)
        self._cache[weakref.ref(instance_cls, self._cache_remove)] = out
        return out


class SimpleAttrRegistryCache(AttrRegistryCache[K, V, dict[str, tuple[K, V]]], ta.Generic[K, V]):
    def __init__(self, registry: AttrRegistry[K, V]) -> None:
        super().__init__(registry, lambda _, dct: dct)
