"""
TODO:
 - DictReg.weak? key/val? currently _cannot remove_
 - *ordering* - insert
  - diverging usecases: insert_after w/ arbitrary obj key and retrieval via linear scan *vs* conventional mapping
   - naw: del is wrap with overriding null-obj, moving is wrap with new order, etc
 - [Mutable]Registry?
"""
import abc
import typing as ta
import weakref

from .. import check
from .. import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')
Listener = ta.Callable[['Registry'], None]


class MISSING(lang.Marker):
    pass


class AlreadyRegisteredException(Exception):
    pass


class AmbiguouslyRegisteredException(Exception):
    pass


class NotRegisteredException(Exception):
    pass


class FrozenRegistrationException(Exception):
    pass


class Registry(lang.Abstract, ta.Mapping[K, V]):

    @abc.abstractproperty
    def version(self) -> ta.Any:
        raise NotImplementedError

    def __setitem__(self, k: K, v: V) -> None:
        self.register(k, v)

    @abc.abstractmethod
    def __getitem__(self, k: K) -> V:
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[K]:
        raise NotImplementedError

    @abc.abstractmethod
    def __contains__(self, o: object) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def items(self) -> ta.AbstractSet[ta.Tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def keys(self) -> ta.AbstractSet[K]:
        raise NotImplementedError

    @abc.abstractmethod
    def values(self) -> ta.ValuesView[V]:
        raise NotImplementedError

    def get(self, key: K, default: ta.Union[V, ta.Any, None] = None) -> ta.Union[V, ta.Any]:
        try:
            return self[key]
        except NotRegisteredException:
            return default

    @abc.abstractmethod
    def register_many(self, dct: ta.Mapping[K, V]) -> 'Registry[K, V]':
        raise NotImplementedError

    def register(self, k: K, v: V) -> 'Registry[K, V]':
        check.not_none(k)
        return self.register_many({k: v})

    def registering(self, *ks: K) -> 'ta.Callable[[V], V]':
        def inner(v: V) -> V:
            self.register_many({k: v for k in ks})
            return v
        for k in ks:
            check.not_none(k)
        return inner

    @abc.abstractmethod
    def add_listeners(self, listeners_by_obj: ta.Mapping[ta.Any, Listener]) -> None:
        raise NotImplementedError

    def add_listener(self, obj: ta.Any, listener: Listener) -> None:
        self.add_listeners({obj: listener})

    @abc.abstractmethod
    def remove_listeners(self, objs: ta.Iterable[ta.Any]) -> None:
        raise NotImplementedError

    def remove_listener(self, obj: ta.Any) -> None:
        self.remove_listener([obj])


class MultiRegistry(Registry[K, ta.AbstractSet[V]], lang.Abstract):
    pass


class BaseRegistry(Registry[K, V], lang.Abstract):

    def __init__(
            self,
            lock: lang.DefaultLockable = None,
            listeners_by_obj: ta.Optional[ta.Mapping[ta.Any, Listener]] = None,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)  # type: ignore

        self._lock = lang.default_lock(lock, True)

        self._listeners_by_obj: ta.MutableMapping[ta.Any, Listener] = weakref.WeakKeyDictionary()
        for obj, listener in (listeners_by_obj or {}).items():
            self.add_listener(obj, listener)

    __hash__ = object.__hash__

    def add_listeners(self, listeners_by_obj: ta.Mapping[ta.Any, Listener]) -> None:
        listeners_by_obj = dict(listeners_by_obj)
        if not listeners_by_obj:
            return
        for obj, listener in listeners_by_obj.items():
            check.not_none(obj)
            check.callable(listener)

        with self._lock():
            for obj in listeners_by_obj.keys():
                if obj in self._listeners_by_obj:
                    raise KeyError(obj)
            for obj, listener in listeners_by_obj.items():
                self._listeners_by_obj[obj] = listener

    def remove_listeners(self, objs: ta.Iterable[ta.Any]) -> None:
        objs = list(objs)
        if not objs:
            return
        for obj in objs:
            check.not_none(obj)

        with self._lock():
            for obj in objs:
                if obj not in objs:
                    raise KeyError(obj)
            for obj in objs:
                del self._listeners_by_obj[obj]

    def _notify_listeners(self) -> None:
        for listener in self._listeners_by_obj.values():
            listener(self)
