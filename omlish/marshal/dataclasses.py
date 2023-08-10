"""
TODO:
 - cfg naming
"""
import collections.abc
import dataclasses as dc
import typing as ta

from .. import check
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


@dc.dataclass(frozen=True)
class Field:
    name: str | None = None


@dc.dataclass(frozen=True)
class DataclassMarshaler(Marshaler):
    flds: ta.Sequence[ta.Tuple[str, Marshaler, str]]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return {k: m.marshal(ctx, getattr(o, a)) for a, m, k in self.flds}


class DataclassMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Optional[Marshaler]:
        if isinstance(rty, type) and dc.is_dataclass(rty):
            flds: list[ta.Tuple[str, Marshaler, str]] = []
            th = ta.get_type_hints(rty)
            for fld in dc.fields(rty):
                fty = th[fld.name]
                m = ctx.make(fty)
                k = fld.name
                if (mdf := fld.metadata.get(Field)) is not None:
                    if mdf.name is not None:
                        k = mdf.name
                flds.append((fld.name, m, k))
            return DataclassMarshaler(flds)
        return None


@dc.dataclass(frozen=True)
class DataclassUnmarshaler(Unmarshaler):
    cls: type
    flds: ta.Sequence[ta.Tuple[str, Unmarshaler, str]]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        ma = check.isinstance(v, collections.abc.Mapping)
        return self.cls(**{a: u.unmarshal(ctx, ma[k]) for k, u, a in self.flds})  # type: ignore


class DataclassUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Optional[Unmarshaler]:
        if isinstance(rty, type) and dc.is_dataclass(rty):
            flds: list[ta.Tuple[str, Unmarshaler, str]] = []
            th = ta.get_type_hints(rty)
            for fld in dc.fields(rty):
                fty = th[fld.name]
                u = ctx.make(fty)
                k = fld.name
                if (mdf := fld.metadata.get(Field)) is not None:
                    if mdf.name is not None:
                        k = mdf.name
                flds.append((k, u, fld.name))
            return DataclassUnmarshaler(rty, flds)
        return None
