import dataclasses as dc
import typing as ta

from ...specs import FieldSpec
from ...specs import FieldType
from ...specs import ReprFn
from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.globals import REPRLIB_RECURSIVE_REPR_GLOBAL
from ..generation.ops import AddMethodOp
from ..generation.ops import Op
from ..generation.ops import OpRef
from ..generation.ops import Ref
from ..generation.registry import register_generator_type
from ..processing.base import ProcessingContext
from .fields import InitFields


##


@dc.dataclass(frozen=True, kw_only=True)
class ReprPlan(Plan):
    @dc.dataclass(frozen=True, kw_only=True)
    class Field:
        name: str
        kw_only: bool = False
        fn: OpRef[ReprFn] | None = None

    fields: tuple[Field, ...]

    id: bool = False
    terse: bool = False
    default_fn: OpRef[ReprFn] | None = None


@register_generator_type(ReprPlan)
class ReprGenerator(Generator[ReprPlan]):
    def plan(self, ctx: ProcessingContext) -> PlanResult[ReprPlan] | None:
        if not ctx.cs.repr or '__repr__' in ctx.cls.__dict__:
            return None

        ifs = ctx[InitFields]
        fs: ta.Sequence[FieldSpec]
        if ctx.cs.terse_repr:
            # If terse repr will match init param order
            fs = ifs.all
        else:
            # Otherwise default to dc.fields() order
            fs = sorted(ctx.cs.fields, key=lambda f: f.repr_priority or 0)

        orm = {}
        rfs: list[ReprPlan.Field] = []
        for i, f in enumerate(fs):
            if not (f.field_type is FieldType.INSTANCE and f.repr):
                continue

            fnr: OpRef | None = None
            if f.repr_fn is not None:
                fnr = OpRef(f'repr.fns.{i}.fn')
                orm[fnr] = f.repr_fn

            rfs.append(ReprPlan.Field(
                name=f.name,
                kw_only=f in ifs.kw_only,
                fn=fnr,
            ))

        drf: OpRef | None = None
        if ctx.cs.default_repr_fn is not None:
            drf = OpRef(f'repr.default_fn')
            orm[drf] = ctx.cs.default_repr_fn

        return PlanResult(
            ReprPlan(
                fields=tuple(rfs),
                id=ctx.cs.repr_id,
                terse=ctx.cs.terse_repr,
                default_fn=drf,
            ),
            orm,
        )

    def generate(self, pl: ReprPlan) -> ta.Iterable[Op]:
        ors: set[Ref] = {REPRLIB_RECURSIVE_REPR_GLOBAL}

        part_lines: list[str] = []

        for f in pl.fields:
            pfx = ''
            if not (pl.terse and not f.kw_only):
                pfx = f'{f.name}='

            fn: OpRef[ReprFn] | None = None
            if f.fn is not None:
                fn = f.fn
            elif pl.default_fn is not None:
                fn = pl.default_fn

            if fn is not None:
                ors.add(fn)
                part_lines.extend([
                    f'    if (s := {fn.ident()}(self.{f.name})) is not None:',
                    f'        parts.append(f"{pfx}{{s}}")',
                ])
            else:
                part_lines.append(
                    f'    parts.append(f"{pfx}{{self.{f.name}!r}}")',
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
