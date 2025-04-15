import dataclasses as dc
import typing as ta

from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.globals import REPRLIB_RECURSIVE_REPR_GLOBAL
from ..generation.ops import AddMethodOp
from ..generation.ops import Ref
from ..generation.ops import Op
from ..generation.ops import OpRef
from ..generation.registry import register_generator_type
from ..processing.base import ProcessingContext
from ..specs import FieldType
from ..specs import ReprFn


##


@dc.dataclass(frozen=True)
class ReprPlan(Plan):
    fields: tuple[str, ...]

    @dc.dataclass(frozen=True)
    class Fn:
        field: str
        fn: OpRef[ReprFn]

    fns: tuple[Fn, ...] = ()

    id: bool = False


@register_generator_type(ReprPlan)
class ReprGenerator(Generator[ReprPlan]):
    def plan(self, ctx: ProcessingContext) -> PlanResult[ReprPlan] | None:
        if not ctx.cs.repr or '__repr__' in ctx.cls.__dict__:
            return None

        fs = sorted(ctx.cs.fields, key=lambda f: f.repr_priority or 0)

        orm = {}
        rfs: list[ReprPlan.Fn] = []
        for i, f in enumerate(fs):
            if f.repr_fn is None:
                continue
            r: OpRef = OpRef(f'repr.fns.{i}.fn')
            orm[r] = f.repr_fn
            rfs.append(ReprPlan.Fn(f.name, r))

        return PlanResult(
            ReprPlan(
                fields=tuple(f.name for f in fs if f.field_type is FieldType.INSTANCE and f.repr),
                fns=tuple(rfs),
                id=ctx.cs.repr_id,
            ),
            orm,
        )

    def generate(self, pl: ReprPlan) -> ta.Iterable[Op]:
        ors: set[Ref] = {REPRLIB_RECURSIVE_REPR_GLOBAL}

        part_lines: list[str] = []

        rfd = {rf.field: rf.fn for rf in pl.fns}
        for f in pl.fields:
            if (rf := rfd.get(f)) is not None:
                ors.add(rf)
                part_lines.extend([
                    f'    if (s := {rf.ident()}(self.{f})) is not None:',
                    f'        parts.append(f"{f}={{s}}")',
                ])
            else:
                part_lines.append(
                    f'    parts.append(f"{f}={{self.{f}!r}}")',
                )

        return [
            AddMethodOp(
                '__repr__',
                '\n'.join([
                    f'@{REPRLIB_RECURSIVE_REPR_GLOBAL.ident}()',
                    f'def __repr__(self):',
                    f'    parts = []',
                    *part_lines,
                    f'    return (',
                    f'        f"{{self.__class__.__qualname__}}{'@{hex(id(self))[2:]}' if pl.id else ''}("',
                    f'        f"{{\', \'.join(parts)}}"',
                    f'        f")"',
                    f'    )',
                ]),
                frozenset(ors),
            ),
        ]
