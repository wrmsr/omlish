import dataclasses as dc
import typing as ta

from ..idents import CLS_IDENT
from ..ops import AddMethodOp
from ..ops import Op
from ..specs import FieldType
from .base import Generator
from .base import Plan
from .base import PlanContext
from .base import PlanResult
from .registry import register_generator_type
from .utils import build_attr_kwargs_str


##


@dc.dataclass(frozen=True)
class CopyPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(CopyPlan)
class CopyGenerator(Generator[CopyPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[CopyPlan] | None:
        if '__copy__' in ctx.cls.__dict__:
            return None

        return PlanResult(CopyPlan(
            tuple(f.name for f in ctx.cs.fields if f.field_type is not FieldType.CLASS),
        ))

    def generate(self, pl: CopyPlan) -> ta.Iterable[Op]:
        lines = [
            f'def __copy__(self):',
            f'    if self.__class__ is not {CLS_IDENT}:',
            f'        raise TypeError(self)',
            f'    return {CLS_IDENT}({build_attr_kwargs_str('self', *pl.fields)})',
        ]

        return [AddMethodOp('__copy__', '\n'.join(lines))]
