import dataclasses as dc
import typing as ta

from ..ops import AddMethodOp
from ..ops import Op
from .base import Generator
from .base import Plan
from .base import PlanContext
from .base import PlanResult
from .registry import register_generator_type
from .utils import build_attr_tuple_str


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

        self_tuple = build_attr_tuple_str('self', *pl.fields)
        other_tuple = build_attr_tuple_str('other', *pl.fields)

        for name, op in NAME_OP_PAIRS:
            ops.append(AddMethodOp(
                name,
                '\n'.join([
                    f'def {name}(self, other):',
                    f'    if other.__class__ is self.__class__:',
                    f'        return {self_tuple} {op} {other_tuple}',
                    f'    return NotImplemented',
                ]),
            ))

        return ops
