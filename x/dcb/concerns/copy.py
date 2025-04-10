import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..generators.utils import build_attr_kwargs_body_src_lines
from ..generators.idents import CLS_IDENT
from ..generators.ops import AddMethodOp
from ..generators.ops import Op
from ..specs import FieldType


##


@dc.dataclass(frozen=True)
class CopyPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(CopyPlan)
class CopyGenerator(Generator[CopyPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[CopyPlan] | None:
        if '__copy__' in ctx.cls.__dict__:
            return None

        return PlanResult(CopyPlan(
            tuple(f.name for f in ctx.cs.fields if f.field_type is not FieldType.CLASS),
        ))

    def generate(self, pl: CopyPlan) -> ta.Iterable[Op]:
        return_lines: list[str]
        if pl.fields:
            return_lines = [
                f'    return {CLS_IDENT}(  # noqa',
                *build_attr_kwargs_body_src_lines(
                    'self',
                    *pl.fields,
                    prefix='        ',
                ),
                f'    )',
            ]
        else:
            return_lines = [
                f'    return {CLS_IDENT}()  # noqa',
            ]

        lines = [
            f'def __copy__(self):',
            f'    if self.__class__ is not {CLS_IDENT}:',
            f'        raise TypeError(self)',
            *return_lines,
        ]

        return [AddMethodOp('__copy__', '\n'.join(lines))]
