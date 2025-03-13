import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..idents import SELF_IDENT
from ..idents import NONE_IDENT
from ..idents import VALUE_IDENT
from ..ops import AddMethodOp
from ..ops import Op
from ..ops import OpRef
from ..types import ReprFn


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
                f.annotation,
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
        for f in pl.fields:
            get_src = '\n'.join([
                f'def {f}({SELF_IDENT}) -> {f.annotation.ident()}:'
                f'    return {SELF_IDENT}.__dict__[{f.name!r}',
            ])

            if not pl.frozen:
                set_src = '\n'.join([
                    f'def {f}({SELF_IDENT}, {VALUE_IDENT}) -> {NONE_IDENT}:',
                ])
                setter = create_fn(
                    f.name,
                    (self_name, f'{f.name}: __dataclass_type_{f.name}__'),
                    [
                        field_assign(
                            self._info.params.frozen,
                            f.name,
                            f.name,
                            self_name,
                            True,
                        ),
                    ],
                    globals=self._info.globals,
                    locals={f'__dataclass_type_{f.name}__': f.type},
                    return_type=lang.just(None),
                )
                prop = prop.setter(setter)

            set_new_attribute(
                self._cls,
                f.name,
                prop,
            )
