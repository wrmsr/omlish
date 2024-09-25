"""
TODO:
 - ensure import order or at least warn or smth lol
 - raise exception on ambiguous 'registered' impls
"""
import collections.abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import marshal as msh
from .. import reflect as rfl
from .secrets import Secret
from .secrets import SecretRef
from .secrets import SecretRefOrStr


class StrOrSecretRefMarshalerUnmarshaler(msh.Marshaler, msh.Unmarshaler):
    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if isinstance(o, str):
            return o
        elif isinstance(o, SecretRef):
            return {'secret': o.key}
        else:
            raise TypeError(o)

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        if isinstance(v, str):
            return v
        elif isinstance(v, collections.abc.Mapping):
            [(mk, mv)] = v.items()
            if mk != 'secret':
                raise TypeError(v)
            return SecretRef(check.isinstance(mv, str))
        else:
            raise TypeError(v)


@dc.field_modifier
def marshal_secret_field(f: dc.Field) -> dc.Field:
    """Mostly obsolete with auto-registration below."""

    return dc.update_field_metadata(f, {
        msh.FieldMetadata: dc.replace(
            f.metadata.get(msh.FieldMetadata, msh.FieldMetadata()),
            marshaler=StrOrSecretRefMarshalerUnmarshaler(),
            unmarshaler=StrOrSecretRefMarshalerUnmarshaler(),
        ),
    })


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
        msh.ForbiddenTypeMarshalerFactory({Secret}),
        msh.TypeMapMarshalerFactory({
            rfl.type_(SecretRefOrStr): StrOrSecretRefMarshalerUnmarshaler(),
        }),
    ]

    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
        msh.ForbiddenTypeUnmarshalerFactory({Secret}),
        msh.TypeMapUnmarshalerFactory({
            rfl.type_(SecretRefOrStr): StrOrSecretRefMarshalerUnmarshaler(),
        }),
    ]
