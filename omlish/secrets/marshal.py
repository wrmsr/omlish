"""
TODO:
 - auto-register forbidden factory for Secret
 - auto-register union - need consistent placement in marshal - raise exception on ambiguous 'registered' impls
"""
import collections.abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import marshal as msh
from .secrets import SecretRef


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
    return dc.update_field_metadata(f, {
        msh.FieldMetadata: dc.replace(
            f.metadata.get(msh.FieldMetadata, msh.FieldMetadata()),
            marshaler=StrOrSecretRefMarshalerUnmarshaler(),
            unmarshaler=StrOrSecretRefMarshalerUnmarshaler(),
        ),
    })
