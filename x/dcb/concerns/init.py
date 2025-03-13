import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..idents import NONE_IDENT
from ..idents import OBJECT_SETATTR_IDENT
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

    fields: tuple[Field, ...]
    frozen: bool


@register_generator_type(InitPlan)
class InitGenerator(Generator[InitPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[InitPlan] | None:
        orm = {}

        bfs: list[InitPlan.Field] = []
        for i, fs in enumerate(ctx.cs.fields):
            r: OpRef = OpRef(f'init.fields.{i}.annotation')
            orm[r] = fs.annotation
            bfs.append(InitPlan.Field(
                fs.name,
                r,
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
            if bs.frozen:
                lines.append(f'    {OBJECT_SETATTR_IDENT}({SELF_IDENT}, {f.name!r}, {f.name})')
            else:
                lines.append(f'    {SELF_IDENT}.{f.name} = {f.name}')
        if not bs.fields:
            lines.append(
                '    pass',
            )

        return [
            AddMethodOp('__init__', '\n'.join(lines), frozenset(ors)),
        ]
