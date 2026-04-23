"""
FIXME: lol do we cache everything it ever sees by identity?
 - yes, but, only keyed by rty - we don't really 'do' temp / weakref classes
  - maybe: still merge and cache, but only via identity IFF there's actually any identity keys in there for the thing

TODO:
 - update interface first to return tv's
 - squash to one big dict, use lang.Identity() wrappers
 - give .register tv.update kwargs, just call that
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


#


ConfigValues: ta.TypeAlias = tv.TypedValues[Config]

_EMPTY_CONFIG_VALUES = ConfigValues()


##


class Configs(lang.Abstract):
    @abc.abstractmethod
    def get(
            self,
            key: ta.Any = None,
            *,
            identity: bool | None = None,
    ) -> ConfigValues:
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

        self._state: ConfigRegistry._State = self._State()

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

    @dc.dataclass(frozen=True, kw_only=True)
    class _State:
        dct: ta.Mapping[ta.Any, ConfigValues] = dc.field(default_factory=dict)
        version: int = 0

        #

        def update(
                self,
                key: ta.Any,
                *items: Config,
                identity: bool = False,
                discard: ta.Literal['all'] | ta.Iterable[type] | None = None,
                mode: ta.Literal['append', 'prepend', 'override', 'default'] = 'append',
        ) -> ConfigRegistry._State:
            if not items:
                return self

            if identity:
                key = lang.Identity(key)

            try:
                xv = self.dct[key]
            except KeyError:
                xv = _EMPTY_CONFIG_VALUES

            nr = xv.update(
                *items,
                discard=discard,
                mode=mode,
            )

            return ConfigRegistry._State(
                dct={**self.dct, key: nr},
                version=self.version + 1,
            )

        #

        _get_merged_cache: dict[ta.Any, ConfigValues] = dc.field(default_factory=dict)

        def get(
                self,
                key: ta.Any = None,
                *,
                identity: bool | None = None,
        ) -> ConfigValues:
            if key is None:
                check.state(identity is not True)
                identity = False

            if identity is None:
                try:
                    return self._get_merged_cache[key]
                except KeyError:
                    pass

                if (idc := self.get(key, identity=True)):
                    ret = self._get_merged_cache[key] = ConfigValues(
                        *self.get(key, identity=False),
                        *idc,
                        override=True,
                    )
                    return ret

            if identity:
                key = lang.Identity(key)

            try:
                return self.dct[key]
            except KeyError:
                return _EMPTY_CONFIG_VALUES

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

    def update(
            self,
            key: ta.Any,
            *items: Config,
            identity: bool = False,
            discard: ta.Literal['all'] | ta.Iterable[type] | None = None,
            mode: ta.Literal['append', 'prepend', 'override', 'default'] = 'append',
    ) -> ta.Self:
        check.arg(not (key is None and identity))

        if not items:
            return self

        with self._lock:
            if self._sealed:
                raise ConfigRegistrySealedError(self)

            self._state = self._state.update(
                key,
                *items,
                identity=identity,
                discard=discard,
                mode=mode,
            )

        return self

    #

    def get(
            self,
            key: ta.Any = None,
            *,
            identity: bool | None = None,
    ) -> ConfigValues:
        return self._state.get(key, identity=identity)
