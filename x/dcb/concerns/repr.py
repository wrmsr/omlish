import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..ops import AddMethodOp
from ..ops import Op
from ..ops import OpRef


##


@dc.dataclass(frozen=True)
class ReprPlan(Plan):
    fields: tuple[str, ...]

    @dc.dataclass(frozen=True)
    class ReprFn:
        field: str
        fn: OpRef[ta.Callable[[ta.Any], str | None]]

    repr_fns: tuple[ReprFn, ...] = ()


@register_generator_type(ReprPlan)
class ReprGenerator(Generator[ReprPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[ReprPlan] | None:
        if not ctx.cs.repr or '__repr__' in ctx.cls.__dict__:
            return None

        orm = {}
        rfs: list[ReprPlan.ReprFn] = []
        for i, f in enumerate(ctx.cs.fields):
            if f.repr_fn is None:
                continue
            r: OpRef = OpRef(f'repr.repr_fns.{i}.fn')
            orm[r] = f.repr_fn
            rfs.append(ReprPlan.ReprFn(f.name, r))

        return PlanResult(
            ReprPlan(
                tuple(f.name for f in ctx.cs.fields),
                tuple(rfs),
            ),
            orm,
        )

    def generate(self, pl: ReprPlan) -> ta.Iterable[Op]:
        repr_lines: list[str] = [
            f'    f"{{self.__class__.__name__}}("',
        ]

        for i, f in enumerate(pl.fields):
            repr_lines.append(
                f'    f"{f}={{self.{f}!r}}{', ' if i < len(pl.fields) - 1 else ''}"',
            )

        repr_lines.append('    f")"')

        return [
            AddMethodOp(
                '__repr__',
                '\n'.join([
                    f'def __repr__(self):',
                    f'    return (',
                    *repr_lines,
                    f'    )',
                ]),
            ),
        ]
