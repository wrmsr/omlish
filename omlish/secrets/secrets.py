import abc
import logging
import os
import typing as ta

from .. import dataclasses as dc
from .. import lang


log = logging.getLogger(__name__)


##


@dc.dataclass(frozen=True)
class Secret:
    key: str


def secret_repr(o: str | Secret | None) -> str | None:
    if isinstance(o, str):
        return '...'
    elif isinstance(o, Secret):
        return repr(o)
    else:
        return None


##


class Secrets(lang.Abstract):
    def fix(self, obj: str | Secret) -> str:
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, Secret):
            return self.get(obj.key)
        else:
            raise TypeError(obj)

    @abc.abstractmethod
    def get(self, key: str) -> str:
        raise NotImplementedError


##


class EmptySecrets(Secrets):
    def get(self, key: str) -> str:
        raise KeyError(key)


EMPTY_SECRETS = EmptySecrets()


##


class SimpleSecrets(Secrets):
    def __init__(self, dct: ta.Mapping[str, str]) -> None:
        super().__init__()
        self._dct = dct

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({{{", ".join(map(repr, self._dct.keys()))}}})'

    def get(self, key: str) -> str:
        return self._dct[key]


##


class CompositeSecrets(Secrets):
    def __init__(self, *children: Secrets) -> None:
        super().__init__()
        self._children = children

    def get(self, key: str) -> str:
        for c in self._children:
            try:
                return c.get(key)
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

    def get(self, key: str) -> str:
        self._log.info('Attempting to access secret: %s', key)
        try:
            ret = self._child.get(key)
        except KeyError:
            self._log.info('Failed to access secret: %s', key)
            raise
        else:
            self._log.info('Successfully accessed secret: %s', key)
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

    def get(self, key: str) -> str:
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
