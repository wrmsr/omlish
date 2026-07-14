import dataclasses as dc
import typing as ta

from ...specs import FieldType
from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.idents import CLS_IDENT
from ..generation.ops import AddMethodOp
from ..generation.ops import Op
from ..generation.registry import register_generator_type
from ..generation.utils import build_attr_kwargs_body_src_lines
from ..processing.base import ProcessingContext


##


@dc.dataclass(frozen=True)
class CopyPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(CopyPlan)
class CopyGenerator(Generator[CopyPlan]):
    def plan(self, ctx: ProcessingContext) -> PlanResult[CopyPlan] | None:
        if '__copy__' in ctx.cls.__dict__:
            return None

        return PlanResult(CopyPlan(
            tuple(f.name for f in ctx.cs.fields if f.field_type is not FieldType.CLASS_VAR),
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

        return [
            AddMethodOp(
                '__copy__',
                '\n'.join(lines),
            ),
        ]
