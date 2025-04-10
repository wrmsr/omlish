import dataclasses as dc
import typing as ta

from ..generators.base import Generator
from ..generators.base import Plan
from ..generators.base import PlanContext
from ..generators.base import PlanResult
from ..generators.registry import register_generator_type
from ..generators.utils import build_attr_tuple_body_src_lines
from ..generators.ops import AddMethodOp
from ..generators.ops import Op


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
    def plan(self, ctx: PlanContext) -> PlanResult[OrderPlan] | None:
        if not ctx.cs.order:
            return None

        for name, _ in NAME_OP_PAIRS:
            if name in ctx.cls.__dict__:
                raise TypeError(
                    f'Cannot overwrite attribute {name} in class {ctx.cls.__name__}. '
                    f'Consider using functools.total_ordering',
                )

        return PlanResult(OrderPlan(
            tuple(f.name for f in ctx.ana.instance_fields if f.compare),
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
                    f'        return True',
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
