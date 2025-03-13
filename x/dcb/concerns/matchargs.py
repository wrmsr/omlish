import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..ops import Op


##


@dc.dataclass(frozen=True)
class MatchArgsPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(MatchArgsPlan)
class MatchArgsGenerator(Generator[MatchArgsPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[MatchArgsPlan] | None:
        # if not self._info.params.match_args:
        #     return
        #
        # ifs = get_init_fields(self._info.fields.values())
        # set_new_attribute(self._cls, '__match_args__', tuple(f.name for f in ifs.std))

        raise NotImplementedError

    def generate(self, pl: MatchArgsPlan) -> ta.Iterable[Op]:
        raise NotImplementedError
