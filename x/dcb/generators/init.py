import dataclasses as dc
import typing as ta

from ..idents import NONE_IDENT
from ..idents import OBJECT_SETATTR_IDENT
from ..idents import SELF_IDENT
from ..ops import AddMethodOp
from ..ops import Op
from ..ops import OpRef
from ..specs import ClassSpec
from .base import Generator
from .base import Plan
from .base import PlanResult
from .registry import register_generator_type


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
    def plan(self, cls: type, cs: ClassSpec) -> PlanResult[InitPlan] | None:
        orm = {}

        bfs: list[InitPlan.Field] = []
        for i, fs in enumerate(cs.fields):
            r: OpRef = OpRef(f'init.fields.{i}.annotation')
            orm[r] = fs.annotation
            bfs.append(InitPlan.Field(
                fs.name,
                r,
            ))

        return PlanResult(
            InitPlan(
                fields=tuple(bfs),
                frozen=cs.frozen,
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
            f'def __init__({", ".join([SELF_IDENT, *params])}) -> {NONE_IDENT}:',
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

        lines.append('')

        return [
            AddMethodOp(name='__init__', src='\n'.join(lines), refs=frozenset(ors)),
        ]
