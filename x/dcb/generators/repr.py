import dataclasses as dc
import typing as ta

from ..ops import AddMethodOp
from ..ops import Op
from .base import Generator
from .base import Plan
from .base import PlanContext
from .base import PlanResult
from .registry import register_generator_type


##


@dc.dataclass(frozen=True)
class ReprPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(ReprPlan)
class ReprGenerator(Generator[ReprPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[ReprPlan] | None:
        if not ctx.cs.repr:
            return None
        return PlanResult(ReprPlan(tuple(f.name for f in ctx.cs.fields)))

    def generate(self, pl: ReprPlan) -> ta.Iterable[Op]:
        repr_fs = ', '.join([f'{f}={{self.{f}}}' for f in pl.fields])
        repr_str = f'f"{{self.__class__.__name__}}({repr_fs})"'
        return [
            AddMethodOp('__repr__', f'def __repr__(self): return {repr_str}'),
        ]
