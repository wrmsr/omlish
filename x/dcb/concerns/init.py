import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..generators.utils import build_setattr_src
from ..idents import NONE_IDENT
from ..idents import SELF_IDENT
from ..ops import AddMethodOp
from ..ops import Op
from ..ops import OpRef


##


@dc.dataclass(frozen=True, kw_only=True)
class InitPlan(Plan):
    @dc.dataclass(frozen=True)
    class Field:
        name: str
        annotation: OpRef[ta.Any]
        override: bool

    fields: tuple[Field, ...]

    frozen: bool


@register_generator_type(InitPlan)
class InitGenerator(Generator[InitPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[InitPlan] | None:
        if '__init__' in ctx.cls.__dict__:
            return None

        orm = {}

        bfs: list[InitPlan.Field] = []
        for i, f in enumerate(ctx.cs.fields):
            r: OpRef = OpRef(f'init.fields.{i}.annotation')
            orm[r] = f.annotation
            bfs.append(InitPlan.Field(
                f.name,
                r,
                f.override or ctx.cs.override,
            ))

        return PlanResult(
            InitPlan(
                fields=tuple(bfs),
                frozen=ctx.cs.frozen,
            ),
            orm,
        )

    def generate(self, bs: InitPlan) -> ta.Iterable[Op]:
        ors: set[OpRef] = set()

        params: list[str] = []
        for f in bs.fields:
            params.append(f'{f.name}: {f.annotation.ident()}')
            ors.add(f.annotation)

        lines = [
            f'def __init__(',
            f'    {SELF_IDENT},',
            *[
                f'    {p},'
                for p in params
            ],
            f') -> {NONE_IDENT}:',
        ]

        for f in bs.fields:
            lines.append(f'    {build_setattr_src(f.name, f.name, frozen=bs.frozen, override=f.override)}')

        if not bs.fields:
            lines.append(
                '    pass',
            )

        return [
            AddMethodOp('__init__', '\n'.join(lines), frozenset(ors)),
        ]
