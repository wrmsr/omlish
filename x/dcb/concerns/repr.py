import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..ops import AddMethodOp
from ..ops import Op


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
            AddMethodOp(
                '__repr__',
                '\n'.join([
                    f'def __repr__(self):',
                    f'    return {repr_str}',
                ]),
            ),
        ]
