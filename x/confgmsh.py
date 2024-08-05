import collections
import copy
import types
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import marshal as msh


##


class field_modifier:  # noqa
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def __ror__(self, other: dc.Field) -> dc.Field:
        return self(other)

    def __call__(self, f: dc.Field) -> dc.Field:
        return check.isinstance(self.fn(check.isinstance(f, dc.Field)), dc.Field)


def update_metadata(old: ta.Mapping, new: ta.Mapping) -> types.MappingProxyType:
    return types.MappingProxyType(collections.ChainMap(new, old))  # type: ignore  # noqa


##


@dc.dataclass(frozen=True)
class Secret:
    key: str


class StrOrSecretMarshaler(msh.Marshaler):
    def marshal(self, ctx: 'msh.MarshalContext', o: ta.Any) -> msh.Value:
        raise NotImplementedError


class StrOrSecretUnmarshaler(msh.Unmarshaler):
    def unmarshal(self, ctx: 'msh.UnmarshalContext', v: msh.Value) -> ta.Any:
        raise NotImplementedError


@field_modifier
def secret_or_key_field(f: dc.Field) -> dc.Field:
    f = copy.copy(check.isinstance(f, dc.Field))
    f.metadata = update_metadata(f.metadata, {
        msh.FieldMetadata: dc.replace(
            f.metadata.get(msh.FieldMetadata, msh.FieldMetadata()),
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


def _main():
    c0 = Cred('u', 'p')
    print(c0)
    cm = msh.marshal(c0)
    print(cm)
    c1 = msh.unmarshal(cm, Cred)
    print(c1)


if __name__ == '__main__':
    _main()
