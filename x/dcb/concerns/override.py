import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..generators.utils import SetattrSrcBuilder
from ..idents import NONE_IDENT
from ..idents import SELF_IDENT
from ..idents import VALUE_IDENT
from ..ops import AddPropertyOp
from ..ops import Op
from ..ops import OpRef


##


@dc.dataclass(frozen=True)
class OverridePlan(Plan):
    @dc.dataclass(frozen=True)
    class Field:
        name: str
        annotation: OpRef[ta.Any]

    fields: tuple[Field, ...]

    frozen: bool


@register_generator_type(OverridePlan)
class OverrideGenerator(Generator[OverridePlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[OverridePlan] | None:
        orm = {}

        flds: list[OverridePlan.Field] = []
        for i, f in enumerate(ctx.ana.instance_fields):
            if not (f.override or ctx.cs.override):
                continue
            r: OpRef = OpRef(f'override.fields.{i}.annotation')
            orm[r] = f.annotation
            flds.append(OverridePlan.Field(
                f.name,
                r,
            ))

        if not flds:
            return None

        return PlanResult(
            OverridePlan(
                tuple(flds),
                ctx.cs.frozen,
            ),
            orm,
        )

    def generate(self, pl: OverridePlan) -> ta.Iterable[Op]:
        ops: list[Op] = []

        for f in pl.fields:
            get_src = '\n'.join([
                f'def {f.name}({SELF_IDENT}) -> {f.annotation.ident()}:',
                f'    return {SELF_IDENT}.__dict__[{f.name!r}]',
            ])

            set_src: str | None = None
            if not pl.frozen:
                set_src = '\n'.join([
                    f'def {f.name}({SELF_IDENT}, {VALUE_IDENT}) -> {NONE_IDENT}:',
                    *[
                        f'    {l}'
                        for l in SetattrSrcBuilder()(f.name, VALUE_IDENT, frozen=pl.frozen, override=True)
                    ],
                ])

            ops.append(AddPropertyOp(
                f.name,
                get_src=get_src,
                set_src=set_src,
                refs=frozenset([f.annotation]),
            ))

        return ops
