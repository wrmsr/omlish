import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang


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


class EmptySecrets(Secrets):
    def get(self, key: str) -> str:
        raise KeyError(key)


EMPTY_SECRETS = EmptySecrets()


class SimpleSecrets(Secrets):
    def __init__(self, dct: ta.Mapping[str, str]) -> None:
        super().__init__()
        self._dct = dct

    def get(self, key: str) -> str:
        return self._dct[key]
