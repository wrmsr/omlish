"""
FIXME: lol do we cache everything it ever sees by identity?
TODO:
 - update interface first to return tv's
 - squash to one big dict, use lang.Identity() wrappers
 - still merge and cache, but only via identity IFF there's actually any identity keys in there for the thing
"""
import abc
import dataclasses as dc
import threading
import typing as ta

from ... import check
from ... import lang
from ... import typedvalues as tv


ConfigT = ta.TypeVar('ConfigT', bound='Config')


##


class Config(tv.TypedValue, lang.Abstract):
    pass


##


class Configs(lang.Abstract):
    @abc.abstractmethod
    def get(
            self,
            key: ta.Any,
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[Config]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_of(
            self,
            key: ta.Any,
            item_ty: type[ConfigT],
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[ConfigT]:
        raise NotImplementedError


##


class ConfigRegistrySealedError(Exception):
    pass


class ConfigRegistry(Configs):
    def __init__(
            self,
            *,
            lock: ta.Optional[threading.RLock] = None,  # noqa
    ) -> None:
        super().__init__()

        if lock is None:
            lock = threading.RLock()
        self._lock = lock

        self._state: ConfigRegistry._State = self._State(
            dct={},
            id_dct={},
            version=0,
        )

        self._sealed = False

    #

    def copy(
            self,
            *,
            lock: ta.Optional[threading.RLock] = None,  # noqa
    ) -> ta.Self:
        ret: ta.Any = type(self)(lock=lock)
        ret._state = self._state  # noqa
        return ret

    #

    @dc.dataclass(frozen=True)
    class _KeyItems:
        key: ta.Any
        items: ta.Sequence[Config] = ()
        item_lists_by_ty: ta.Mapping[type[Config], ta.Sequence[Config]] = dc.field(default_factory=dict)

        #

        def add(self, *items: Config) -> ConfigRegistry._KeyItems:
            if not items:
                return self

            item_lists_by_ty: dict[type[Config], list[Config]] = {}

            for i in items:
                it = type(i)
                if (iut := issubclass(it, tv.UniqueTypedValue)):
                    check.not_in(it, self.item_lists_by_ty)
                try:
                    l = item_lists_by_ty[it]
                except KeyError:
                    l = item_lists_by_ty[it] = list(self.item_lists_by_ty.get(it, ()))
                else:
                    check.state(not iut)
                l.append(i)

            return ConfigRegistry._KeyItems(
                self.key,
                (*self.items, *items),
                {**self.item_lists_by_ty, **item_lists_by_ty},
            )

        def remove(self, *tys: type[Config]) -> ConfigRegistry._KeyItems:
            if not tys:
                return self

            ty_set = set(tys)
            if not any(ty in ty_set for ty in self.item_lists_by_ty):
                return self

            return ConfigRegistry._KeyItems(
                self.key,
                tuple(i for i in self.items if type(i) not in ty_set),
                {
                    ty: l
                    for ty, l in self.item_lists_by_ty.items()
                    if ty not in ty_set
                },
            )

    @dc.dataclass(frozen=True, kw_only=True)
    class _State:
        dct: ta.Mapping[ta.Any, ConfigRegistry._KeyItems]
        id_dct: ta.Mapping[ta.Any, ConfigRegistry._KeyItems]
        version: int

        #

        def register(
                self,
                key: ta.Any,
                *items: Config,
                identity: bool = False,
                replace: bool = False,
        ) -> ConfigRegistry._State:
            if not items:
                return self

            sr_dct: ta.Any = self.dct if not identity else self.id_dct
            sr: ConfigRegistry._KeyItems
            if (sr := sr_dct.get(key)) is not None:
                if replace:
                    sr = sr.remove(*map(type, items))
            else:
                sr = ConfigRegistry._KeyItems(key)
            sr = sr.add(*items)
            new = {key: sr}

            return ConfigRegistry._State(
                dct={**self.dct, **new} if not identity else self.dct,
                id_dct={**self.id_dct, **new} if identity else self.id_dct,
                version=self.version + 1,
            )

        #

        _get_cache: dict[ta.Any, ta.Sequence[Config]] = dc.field(default_factory=dict)

        def get(
                self,
                key: ta.Any,
                *,
                identity: bool | None = None,
        ) -> ta.Sequence[Config]:
            if identity is None:
                try:
                    return self._get_cache[key]
                except KeyError:
                    pass

                ret = self._get_cache[key] = (
                    *self.get(key, identity=True),
                    *self.get(key, identity=False),
                )
                return ret

            dct: ta.Any = self.dct if not identity else self.id_dct
            try:
                return dct[key].items
            except KeyError:
                return ()

        _get_of_cache: dict[ta.Any, dict[type, ta.Sequence[Config]]] = dc.field(default_factory=dict)

        def get_of(
                self,
                key: ta.Any,
                item_ty: type[Config],
                *,
                identity: bool | None = None,
        ) -> ta.Sequence[Config]:
            if identity is None:
                try:
                    return self._get_of_cache[key][item_ty]
                except KeyError:
                    pass

                ret = self._get_of_cache.setdefault(key, {})[item_ty] = (
                    *self.get_of(key, item_ty, identity=True),
                    *self.get_of(key, item_ty, identity=False),
                )
                return ret

            dct: ta.Any = self.dct if not identity else self.id_dct
            try:
                sr = dct[key]
            except KeyError:
                return ()
            return sr.item_lists_by_ty.get(item_ty, ())

    def is_sealed(self) -> bool:
        if self._sealed:
            return True
        with self._lock:
            return self._sealed

    def seal(self) -> ta.Self:
        if self._sealed:
            raise ConfigRegistrySealedError(self)
        with self._lock:
            self._seal()
        return self

    def _seal(self) -> None:
        if self._sealed:
            raise ConfigRegistrySealedError(self)

        self._sealed = True

    #

    def register(
            self,
            key: ta.Any,
            *items: Config,
            identity: bool = False,
            replace: bool = False,
    ) -> ta.Self:
        check.arg(not (key is None and identity))

        if not items:
            return self

        with self._lock:
            if self._sealed:
                raise ConfigRegistrySealedError(self)

            self._state = self._state.register(
                key,
                *items,
                identity=identity,
                replace=replace,
            )

        return self

    #

    def get(
            self,
            key: ta.Any,
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[Config]:
        check.arg(not (key is None and identity))

        return self._state.get(key, identity=identity)

    def get_of(
            self,
            key: ta.Any,
            item_ty: type[ConfigT],
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[ConfigT]:
        check.arg(not (key is None and identity))

        return self._state.get_of(key, item_ty, identity=identity)  # type: ignore[return-value]
