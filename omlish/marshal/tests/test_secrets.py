import abc
import collections.abc
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ..base import MarshalContext
from ..base import Marshaler
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..global_ import marshal
from ..global_ import unmarshal
from ..objects import FieldMetadata
from ..values import Value


##


@dc.dataclass(frozen=True)
class Secret:
    key: str


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


class SimpleSecrets(Secrets):
    def __init_(self, dct: ta.Mapping[str, str]) -> None:
        super().__init__()
        self._dct = dct

    def get(self, key: str) -> str:
        return self._dct[key]


##


class StrOrSecretMarshaler(Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if isinstance(o, str):
            return o
        elif isinstance(o, Secret):
            return {'secret': o.key}
        else:
            raise TypeError(o)


class StrOrSecretUnmarshaler(Unmarshaler):
    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        if isinstance(v, str):
            return v
        elif isinstance(v, collections.abc.Mapping):
            [(mk, mv)] = v.items()
            if mk != 'secret':
                raise TypeError(v)
            return Secret(check.isinstance(mv, str))
        else:
            raise TypeError(v)


@dc.field_modifier
def secret_or_key_field(f: dc.Field) -> dc.Field:
    return dc.update_field_metadata(f, {
        FieldMetadata: dc.replace(
            f.metadata.get(FieldMetadata, FieldMetadata()),
            marshaler=StrOrSecretMarshaler(),
            unmarshaler=StrOrSecretUnmarshaler(),
        ),
    })


##


@dc.dataclass(frozen=True)
class Cred:
    username: str
    password: str | Secret = dc.field() | secret_or_key_field


def test_secrets():
    print()
    for c0 in [
        Cred('u', 'p'),
        Cred('u', Secret('p')),
    ]:
        print(c0)
        cm = marshal(c0)
        print(cm)
        c1 = unmarshal(cm, Cred)
        print(c1)
        print()
