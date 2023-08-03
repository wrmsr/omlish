"""
TODO:
 - cfg naming
"""
import dataclasses as dc
import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .specs import Spec
from .values import Value


@dc.dataclass(frozen=True)
class DataclassMarshaler(Marshaler):
    flds: ta.Sequence[ta.Tuple[str, Marshaler]]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return {k: m.marshal(ctx, getattr(o, k)) for k, m in self.flds}


class DataclassMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if isinstance(spec, type) and dc.is_dataclass(spec):
            flds: list[ta.Tuple[str, Marshaler]] = []
            th = ta.get_type_hints(spec)
            for fld in dc.fields(spec):
                fty = th[fld.name]
                if (m := ctx.make(fty)) is None:
                    return None
                flds.append((fld.name, m))
            return DataclassMarshaler(flds)
        return None


@dc.dataclass(frozen=True)
class DataclassUnmarshaler(Unmarshaler):
    cls: type
    flds: ta.Sequence[ta.Tuple[str, Unmarshaler]]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.cls(**{k: u.unmarshal(ctx, v[k]) for k, u in self.flds})


class DataclassUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, spec: Spec) -> ta.Optional[Unmarshaler]:
        if isinstance(spec, type) and dc.is_dataclass(spec):
            flds: list[ta.Tuple[str, Unmarshaler]] = []
            th = ta.get_type_hints(spec)
            for fld in dc.fields(spec):
                fty = th[fld.name]
                if (u := ctx.make(fty)) is None:
                    return None
                flds.append((fld.name, u))
            return DataclassUnmarshaler(spec, flds)
        return None
