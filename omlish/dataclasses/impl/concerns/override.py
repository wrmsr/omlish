import dataclasses as dc
import typing as ta

from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.globals import NONE_GLOBAL
from ..generation.idents import SELF_IDENT
from ..generation.idents import VALUE_IDENT
from ..generation.ops import AddPropertyOp
from ..generation.ops import Op
from ..generation.ops import OpRef
from ..generation.ops import Ref
from ..generation.registry import register_generator_type
from ..generation.utils import SetattrSrcBuilder
from ..processing.base import ProcessingContext
from .fields import InstanceFields


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
    def plan(self, ctx: ProcessingContext) -> PlanResult[OverridePlan] | None:
        orm = {}

        flds: list[OverridePlan.Field] = []
        for i, f in enumerate(ctx[InstanceFields]):
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
            op_refs: set[Ref] = {f.annotation}

            get_src = '\n'.join([
                f'def {f.name}({SELF_IDENT}) -> {f.annotation.ident()}:',
                f'    return {SELF_IDENT}.__dict__[{f.name!r}]',
            ])

            set_src: str | None = None
            if not pl.frozen:
                sab = SetattrSrcBuilder()
                set_src = '\n'.join([
                    f'def {f.name}({SELF_IDENT}, {VALUE_IDENT}) -> {NONE_GLOBAL.ident}:',
                    *[
                        f'    {l}'
                        for l in sab(
                            f.name,
                            VALUE_IDENT,
                            frozen=pl.frozen,
                            override=True,
                        )
                    ],
                ])
                op_refs.add(NONE_GLOBAL)
                op_refs.update(sab.refs)

            ops.append(AddPropertyOp(
                f.name,
                get_src=get_src,
                set_src=set_src,
                refs=frozenset(op_refs),
            ))

        return ops
