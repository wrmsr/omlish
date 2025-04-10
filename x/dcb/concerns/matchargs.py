import dataclasses as dc
import typing as ta

from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.ops import Op
from ..generation.ops import SetAttrOp
from ..generation.registry import register_generator_type
from ..processing import ProcessingContext
from .fields import InitFields


##


@dc.dataclass(frozen=True)
class MatchArgsPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(MatchArgsPlan)
class MatchArgsGenerator(Generator[MatchArgsPlan]):
    def plan(self, ctx: ProcessingContext) -> PlanResult[MatchArgsPlan] | None:
        if not ctx.cs.match_args or '__match_args__' in ctx.cls.__dict__:
            return None

        return PlanResult(MatchArgsPlan(
            tuple(f.name for f in ctx[InitFields].std),
        ))

    def generate(self, pl: MatchArgsPlan) -> ta.Iterable[Op]:
        return [
            SetAttrOp(
                '__match_args__',
                pl.fields,
                'error',
            ),
        ]
