import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..generators.ops import Op
from ..generators.ops import SetAttrOp
from .fields import InitFields


##


@dc.dataclass(frozen=True)
class MatchArgsPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(MatchArgsPlan)
class MatchArgsGenerator(Generator[MatchArgsPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[MatchArgsPlan] | None:
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
