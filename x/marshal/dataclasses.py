"""
TODO:
 - cfg naming
"""
import dataclasses as dc
import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
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
            flds: ta.List[ta.Tuple[str, Marshaler]] = []
            th = ta.get_type_hints(spec)
            for fld in dc.fields(spec):
                fty = th[fld.name]
                if (m := ctx.make(fty)) is None:
                    return None
                flds.append((fld.name, m))
            return DataclassMarshaler(flds)
        return None
