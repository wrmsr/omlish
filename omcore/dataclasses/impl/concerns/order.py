import dataclasses as dc
import typing as ta

from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.ops import AddMethodOp
from ..generation.ops import Op
from ..generation.registry import register_generator_type
from ..generation.utils import build_attr_tuple_body_src_lines
from ..processing.base import ProcessingContext
from .fields import InstanceFields


##


NAME_OP_PAIRS = [
    ('__lt__', '<'),
    ('__le__', '<='),
    ('__gt__', '>'),
    ('__ge__', '>='),
]


##


@dc.dataclass(frozen=True)
class OrderPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(OrderPlan)
class OrderGenerator(Generator[OrderPlan]):
    def plan(self, ctx: ProcessingContext) -> PlanResult[OrderPlan] | None:
        if not ctx.cs.order:
            return None

        for name, _ in NAME_OP_PAIRS:
            if name in ctx.cls.__dict__:
                raise TypeError(
                    f'Cannot overwrite attribute {name} in class {ctx.cls.__name__}. '
                    f'Consider using functools.total_ordering',
                )

        return PlanResult(OrderPlan(
            tuple(f.name for f in ctx[InstanceFields] if f.compare),
        ))

    def generate(self, pl: OrderPlan) -> ta.Iterable[Op]:
        ops: list[AddMethodOp] = []

        for name, op in NAME_OP_PAIRS:
            ret_lines: list[str] = []
            if pl.fields:
                ret_lines.extend([
                    f'    return (',
                    *build_attr_tuple_body_src_lines(
                        'self',
                        *pl.fields,
                        prefix='        ',
                    ),
                    f'    ) {op} (',
                    *build_attr_tuple_body_src_lines(
                        'other',
                        *pl.fields,
                        prefix='        ',
                    ),
                    f'    )',
                ])
            else:
                ret_lines.append(
                    f'    return {"True" if "=" in op else "False"}',
                )

            ops.append(AddMethodOp(
                name,
                '\n'.join([
                    f'def {name}(self, other):',
                    f'    if other.__class__ is not self.__class__:',
                    f'        return NotImplemented',
                    *ret_lines,
                ]),
            ))

        return ops
