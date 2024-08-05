import typing as ta

from omlish import dataclasses as dc
from omlish import marshal as msh


@dc.dataclass(frozen=True)
class Secret:
    key: str


class StrOrSecretMarshaler(msh.Marshaler):
    def marshal(self, ctx: 'msh.MarshalContext', o: ta.Any) -> msh.Value:
        raise NotImplementedError


class StrOrSecretUnmarshaler(msh.Unmarshaler):
    def unmarshal(self, ctx: 'msh.UnmarshalContext', v: msh.Value) -> ta.Any:
        raise NotImplementedError


_SECRET_OR_KEY_FIELD = {msh.FieldMetadata: msh.FieldMetadata(
    marshaler=StrOrSecretMarshaler(),
    unmarshaler=StrOrSecretUnmarshaler(),
)}


@dc.dataclass(frozen=True)
class Cred:
    username: str
    password: str | Secret = dc.xfield(metadata=_SECRET_OR_KEY_FIELD)


def _main():
    c0 = Cred('u', 'p')
    print(c0)
    cm = msh.marshal(c0)
    print(cm)
    c1 = msh.unmarshal(cm, Cred)
    print(c1)


if __name__ == '__main__':
    _main()
