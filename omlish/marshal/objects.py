"""
TODO:
 - cfg naming
 - adapters for dataclasses / namedtuples / user objects (as confitured)
 - mro-merge ObjectMetadata
"""
import collections.abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .naming import Naming
from .values import Value


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldMetadata:
    name: str | None = None
    alts: ta.Iterable[str] | None = None

    omit_if: ta.Callable[[ta.Any], bool] | None = None

    marshaler: Marshaler | None = None
    marshaler_factory: MarshalerFactory | None = None

    unmarshaler: Unmarshaler | None = None
    unmarshaler_factory: UnmarshalerFactory | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ObjectMetadata:
    field_naming: Naming | None = None

    unknown_field: str | None = None

    field_defaults: FieldMetadata = FieldMetadata()


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldInfo:
    name: str
    type: ta.Any

    marshal_name: str
    unmarshal_names: ta.Sequence[str]

    metadata: FieldMetadata = FieldMetadata()

    omit_if: ta.Callable[[ta.Any], bool] | None = None


##


@dc.dataclass(frozen=True)
class ObjectMarshaler(Marshaler):
    fields: ta.Sequence[tuple[FieldInfo, Marshaler]]
    unknown_field: str | None = None

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        ret = {}
        for fi, m in self.fields:
            v = getattr(o, fi.name)
            if fi.omit_if is not None and fi.omit_if(v):
                continue
            ret[fi.marshal_name] = m.marshal(ctx, v)

        if self.unknown_field is not None:
            if (ukf := getattr(o, self.unknown_field)):
                if (dks := set(ret) & set(ukf)):
                    raise KeyError(f'Unknown field keys duplicate fields: {dks!r}')

            ret.update(ukf)  # FIXME: marshal?

        return ret


##


@dc.dataclass(frozen=True)
class ObjectUnmarshaler(Unmarshaler):
    cls: type
    fields_by_unmarshal_name: ta.Mapping[str, tuple[FieldInfo, Unmarshaler]]
    unknown_field: str | None = None

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        ma = check.isinstance(v, collections.abc.Mapping)
        u: ta.Any
        kw: dict[str, ta.Any] = {}
        ukf: dict[str, ta.Any] | None = None

        if self.unknown_field is not None:
            kw[self.unknown_field] = ukf = {}

        for k, mv in ma.items():
            ks = check.isinstance(k, str)

            try:
                fi, u = self.fields_by_unmarshal_name[ks]

            except KeyError:
                if ukf is not None:
                    ukf[ks] = mv  # FIXME: unmarshal?
                    continue
                raise

            if fi.name in kw:
                raise KeyError(f'Duplicate keys for field {fi.name!r}: {ks!r}')

            kw[fi.name] = u.unmarshal(ctx, mv)

        return self.cls(**kw)
