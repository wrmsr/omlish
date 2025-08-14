import dataclasses as dc
import typing as ta

from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.ops import AddMethodOp
from ..generation.ops import Op
from ..generation.registry import register_generator_type
from ..processing.base import ProcessingContext
from .fields import InstanceFields


##


@dc.dataclass(frozen=True)
class EqPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(EqPlan)
class EqGenerator(Generator[EqPlan]):
    def plan(self, ctx: ProcessingContext) -> PlanResult[EqPlan] | None:
        if not ctx.cs.eq or '__eq__' in ctx.cls.__dict__:
            return None

        return PlanResult(EqPlan(
            tuple(f.name for f in ctx[InstanceFields] if f.compare),
        ))

    def generate(self, pl: EqPlan) -> ta.Iterable[Op]:
        ret_lines: list[str]
        if pl.fields:
            ret_lines = [
                f'    return (',
                *[
                    f'        self.{a} == other.{a}{" and" if i < len(pl.fields) - 1 else ""}'
                    for i, a in enumerate(pl.fields)
                ],
                f'    )',
            ]
        else:
            ret_lines = [
                f'    return True',
            ]

        return [
            AddMethodOp(
                '__eq__',
                '\n'.join([
                    f'def __eq__(self, other):',
                    f'    if self is other:',
                    f'        return True',
                    f'    if self.__class__ is not other.__class__:',
                    f'        return NotImplemented',
                    *ret_lines,
                ]),
            ),
        ]
