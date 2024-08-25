"""
TODO:
 - SqlFunctionSecrets (in .sql?)
 - crypto is just Transformed, bound with a key
 - crypto key in env + values in file?
 - Secret:
  - hold ref to Secret, and key
  - time of retrieval
  - logs accesses
 - types? ssh / url / pw / basicauthtoken / tls / str
"""
import abc
import collections
import logging
import os
import sys
import time
import types  # noqa
import typing as ta

from .. import dataclasses as dc
from .. import lang


log = logging.getLogger(__name__)


##


class Secret(lang.NotPicklable, lang.Final):
    _VALUE_ATTR = '__secret_value__'

    def __init__(self, *, key: str | None, value: str) -> None:
        super().__init__()
        self._key = key
        setattr(self, self._VALUE_ATTR, lambda: value)

    def __repr__(self) -> str:
        return f'Secret<{self._key or ""}>'

    def __str__(self) -> ta.NoReturn:
        raise TypeError

    def reveal(self) -> str:
        return getattr(self, self._VALUE_ATTR)()


##


@dc.dataclass(frozen=True)
class SecretRef:
    key: str


SecretRefOrStr: ta.TypeAlias = SecretRef | str


def secret_repr(o: SecretRefOrStr | None) -> str | None:
    if isinstance(o, str):
        return '...'
    elif isinstance(o, SecretRef):
        return repr(o)
    elif o is None:
        return None
    else:
        raise TypeError(o)


@dc.field_modifier
def secret_field(f: dc.Field) -> dc.Field:
    return dc.update_field_extras(
        f,
        repr_fn=secret_repr,
        unless_non_default=True,
    )


##


class Secrets(lang.Abstract):
    def fix(self, obj: str | SecretRef | Secret) -> Secret:
        if isinstance(obj, Secret):
            return obj
        elif isinstance(obj, str):
            return Secret(key=None, value=obj)
        elif isinstance(obj, SecretRef):
            return self.get(obj.key)
        else:
            raise TypeError(obj)

    def get(self, key: str) -> Secret:
        try:
            raw = self._get_raw(key)  # noqa
        except KeyError:  # noqa
            raise
        else:
            return Secret(key=key, value=raw)

    @abc.abstractmethod
    def _get_raw(self, key: str) -> str:
        raise NotImplementedError


##


class EmptySecrets(Secrets):
    def _get_raw(self, key: str) -> str:
        raise KeyError(key)


EMPTY_SECRETS = EmptySecrets()


##


class MappingSecrets(Secrets):
    def __init__(self, dct: ta.Mapping[str, str]) -> None:
        super().__init__()
        self._dct = dct

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({{{", ".join(map(repr, self._dct.keys()))}}})'

    def _get_raw(self, key: str) -> str:
        return self._dct[key]


##


@dc.dataclass(frozen=True)
class FnSecrets(Secrets):
    fn: ta.Callable[[str], str]

    def _get_raw(self, key: str) -> str:
        return self.fn(key)


##


@dc.dataclass(frozen=True)
class TransformedSecrets(Secrets):
    fn: ta.Callable[[str], str]
    child: Secrets

    def _get_raw(self, key: str) -> str:
        # FIXME: hm..
        return self.fn(self.child._get_raw(key))  # noqa


##


class CachingSecrets(Secrets):
    def __init__(
            self,
            child: Secrets,
            *,
            ttl_s: float | None = None,
            clock: ta.Callable[..., float] = time.time,
    ) -> None:
        super().__init__()
        self._child = child
        self._dct: dict[str, str] = {}
        self._ttl_s = ttl_s
        self._clock = clock
        self._deque: collections.deque[tuple[str, float]] = collections.deque()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({{{", ".join(map(repr, self._dct.keys()))}}})'

    def evict(self) -> None:
        now = self._clock()
        while self._deque:
            k, dl = self._deque[0]
            if now < dl:
                break
            del self._dct[k]
            self._deque.popleft()

    def _get_raw(self, key: str) -> str:
        self.evict()
        try:
            return self._dct[key]
        except KeyError:
            pass
        out = self._child._get_raw(key)  # noqa
        self._dct[key] = out
        if self._ttl_s is not None:
            dl = self._clock() + self._ttl_s
            self._deque.append((key, dl))
        return out


##


class CompositeSecrets(Secrets):
    def __init__(self, *children: Secrets) -> None:
        super().__init__()
        self._children = children

    def _get_raw(self, key: str) -> str:
        for c in self._children:
            try:
                return c._get_raw(key)  # noqa
            except KeyError:
                pass
        raise KeyError(key)


##


class LoggingSecrets(Secrets):
    def __init__(
            self,
            child: Secrets,
            *,
            log: logging.Logger | None = None,  # noqa
    ) -> None:
        super().__init__()
        self._child = child
        self._log = log if log is not None else globals()['log']

    IGNORE_PACKAGES: ta.ClassVar[ta.AbstractSet[str]] = {
        __package__,
    }

    def _get_caller_str(self, n: int = 3) -> str:
        l: list[str] = []
        f: types.FrameType | None = sys._getframe(2)  # noqa
        while f is not None and len(l) < n:
            try:
                pkg = f.f_globals['__package__']
            except KeyError:
                pkg = None
            else:
                if pkg in self.IGNORE_PACKAGES:
                    f = f.f_back
                    continue
            if (fn := f.f_code.co_filename):
                l.append(f'{fn}:{f.f_lineno}')
            else:
                l.append(pkg)
            f = f.f_back
        return ', '.join(l)

    def _get_raw(self, key: str) -> str:
        cs = self._get_caller_str()
        self._log.info('Attempting to access secret: %s, %s', key, cs)
        try:
            ret = self._child._get_raw(key)  # noqa
        except KeyError:
            self._log.info('Failed to access secret: %s, %s', key, cs)
            raise
        else:
            self._log.info('Successfully accessed secret: %s, %s', key, cs)
            return ret


##


class EnvVarSecrets(Secrets):
    def __init__(
            self,
            *,
            env: ta.MutableMapping[str, str] | None = None,
            upcase: bool = False,
            prefix: str | None = None,
            pop: bool = False,
    ) -> None:
        super().__init__()
        self._env = env
        self._upcase = upcase
        self._prefix = prefix
        self._pop = pop

    def _get_raw(self, key: str) -> str:
        ekey = key
        if self._upcase:
            ekey = ekey.upper()
        if self._prefix is not None:
            ekey = self._prefix + ekey
        if self._env is not None:
            dct = self._env
        else:
            dct = os.environ
        if self._pop:
            return dct.pop(ekey)
        else:
            return dct[ekey]
