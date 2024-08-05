import collections.abc
import copy
import typing as ta

from ... import check
from ... import dataclasses as dc
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
    f = copy.copy(check.isinstance(f, dc.Field))
    f.metadata = dc.update_metadata(f.metadata, {
        FieldMetadata: dc.replace(
            f.metadata.get(FieldMetadata, FieldMetadata()),
            marshaler=StrOrSecretMarshaler(),
            unmarshaler=StrOrSecretUnmarshaler(),
        ),
    })
    return f


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
