import collections.abc
import typing as ta

from .. import check
from .. import lang
from .types import AmbiguouslyRegisteredException
from .types import BaseRegistry
from .types import MISSING
from .types import MultiRegistry
from .types import NotRegisteredException
from .types import Registry


K = ta.TypeVar('K')
V = ta.TypeVar('V')


class CompositeRegistry(BaseRegistry[K, V]):

    Policy = ta.Callable[[ta.Iterable[Registry[K, V]]], ta.Mapping[K, V]]

    @lang.staticfunction  # noqa
    @staticmethod
    def FIRST_ONE(children):
        ret = {}
        for child in children:
            for k, v in child.items():
                if k not in ret:
                    ret[k] = v
        return ret

    @lang.staticfunction  # noqa
    @staticmethod
    def ONLY_ONE(children):
        ret = {}
        for child in children:
            for k, v in child.items():
                if k in ret:
                    raise AmbiguouslyRegisteredException(k, ret[k])
                ret[k] = v
        return ret

    def __init__(
            self,
            children: ta.Iterable[Registry[K, V]],
            policy: Policy = FIRST_ONE,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self._children = list(children)
        self._policy = check.callable(policy)

        with self._lock():
            def listener(_):
                with self._lock():
                    self._maybe_build()
                    self._notify_listeners()

            for child in self._children:
                child.add_listener(self, listener)

            self._version = MISSING
            self._maybe_build()

    @property
    def children(self) -> ta.List[Registry[K, V]]:
        return self._children

    def _maybe_build(self) -> ta.Tuple[ta.Any, ta.Mapping[K, V]]:
        with self._lock():
            version = tuple(c.version for c in self._children)
            if version != self._version:
                composed = self._policy(self._children)
                self._composed, self._version = composed, version
                self._notify_listeners()
            else:
                composed = self._composed
            return version, composed

    @property
    def version(self) -> ta.Tuple:
        return self._maybe_build()[0]

    @property
    def composed(self) -> ta.Mapping[K, V]:
        return self._maybe_build()[1]

    def __getitem__(self, k: K) -> V:
        try:
            return self.composed[k]
        except KeyError:
            raise NotRegisteredException(k)

    def __iter__(self) -> ta.Iterator[K]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self.composed)

    def __contains__(self, k: K) -> bool:
        return any(k in c for c in self._children)

    def items(self) -> ta.AbstractSet[ta.Tuple[K, V]]:
        return self.composed.items()

    def keys(self) -> ta.AbstractSet[K]:
        return self.composed.keys()

    def values(self) -> ta.ValuesView[V]:
        return self.composed.values()

    def register_many(self, dct: ta.Mapping[K, V]) -> 'Registry[K, V]':
        raise TypeError


class CompositeMultiRegistry(CompositeRegistry[K, ta.AbstractSet[V]], MultiRegistry[K, V]):

    @lang.staticfunction  # noqa
    @staticmethod
    def MERGE(children):
        ret = {}
        for child in children:
            for k, v in child.items():
                check.isinstance(v, collections.abc.Set)
                try:
                    ret[k].update(v)
                except KeyError:
                    ret[k] = set(v)
        return {k: frozenset(v) for k, v in ret.items()}

    def __init__(
            self,
            children: ta.Iterable[Registry[K, V]],
            *args,
            **kwargs,
    ) -> None:
        children = list(children)
        for child in children:
            check.isinstance(child, MultiRegistry)

        super().__init__(children, *args, **kwargs)
