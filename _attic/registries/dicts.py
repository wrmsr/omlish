import typing as ta

from .. import check
from .. import collections as ocol
from .types import AlreadyRegisteredException
from .types import BaseRegistry
from .types import FrozenRegistrationException
from .types import MultiRegistry
from .types import NotRegisteredException
from .types import Registry


K = ta.TypeVar('K')
V = ta.TypeVar('V')


class DictRegistry(BaseRegistry[K, V]):

    Coercer = ta.Callable[[ta.Mapping[K, V]], ta.Mapping[K, V]]
    Validator = ta.Callable[[ta.Mapping[K, V]], None]

    def __init__(
            self,
            *args,
            frozen: bool = False,
            coercer: ta.Optional[Coercer[K, V]] = None,
            validator: ta.Optional[Validator[K, V]] = None,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self._dct: ta.MutableMapping[K, V] = {}
        self._coercer = check.callable(coercer) if coercer is not None else None
        self._validator = check.callable(validator) if validator is not None else None

        self._version = 0

        self._frozen = False
        items = list(ocol.yield_dict_init(*args))
        if items:
            self.register_many(dict(items), silent=True)
        self._frozen = bool(frozen)
        if items:
            self._notify_listeners()

    def freeze(self) -> bool:
        with self._lock():
            if not self._frozen:
                self._frozen = True
                return True
            else:
                return False

    @property
    def frozen(self) -> bool:
        return self._frozen

    @property
    def version(self) -> int:
        return self._version

    def __getitem__(self, k: K) -> V:
        try:
            return self._dct[k]
        except KeyError:
            raise NotRegisteredException(k)

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self) -> ta.Iterator[K]:
        return iter(self._dct)

    def __contains__(self, o: object) -> bool:
        return o in self._dct

    def items(self) -> ta.AbstractSet[ta.Tuple[K, V]]:
        return self._dct.items()

    def keys(self) -> ta.AbstractSet[K]:
        return self._dct.keys()

    def values(self) -> ta.ValuesView[V]:
        return self._dct.values()

    def _prepare_value(self, k: K, v: V) -> V:
        return v

    def register_many(
            self,
            dct: ta.Mapping[K, V],
            *,
            silent: bool = False,
    ) -> 'Registry[K, V]':
        if self._frozen:
            raise FrozenRegistrationException(self)

        if not dct:
            return self

        with self._lock():
            dct = dict(dct)

            if self._coercer is not None:
                dct = self._coercer(dct)

            if self._validator is not None:
                self._validator(dct)

            ndct = {}

            for k, v in dct.items():
                check.not_none(k)

                try:
                    ov = self._dct[k]
                except KeyError:
                    pass
                else:
                    raise AlreadyRegisteredException(k, v, ov)

                ndct[k] = self._prepare_value(k, v)

            for k, v in ndct.items():
                self._dct[k] = v

            self._version += 1

            if not silent:
                self._notify_listeners()

        return self


class DictMultiRegistry(DictRegistry[K, ta.AbstractSet[V]], MultiRegistry[K, V]):

    def _prepare_value(self, k: K, v: V) -> V:
        check.arg(not isinstance(v, str))
        return frozenset(v)
