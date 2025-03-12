import dataclasses as dc
import typing as ta

from ..idents import CLS_IDENT
from ..idents import FROZEN_INSTANCE_ERROR_IDENT
from ..internals import FIELDS_ATTR
from ..internals import PARAMS_ATTR
from ..ops import AddMethodOp
from ..ops import Op
from .base import Generator
from .base import Plan
from .base import PlanContext
from .base import PlanResult
from .registry import register_generator_type


##


def check_frozen_bases(cls: type, frozen: bool) -> None:
    all_frozen_bases = None
    any_frozen_base = False
    has_dataclass_bases = False

    for b in cls.__mro__[-1:0:-1]:
        base_fields = getattr(b, FIELDS_ATTR, None)
        if base_fields is None:
            continue

        has_dataclass_bases = True
        if all_frozen_bases is None:
            all_frozen_bases = True

        current_frozen = getattr(b, PARAMS_ATTR).frozen
        all_frozen_bases = all_frozen_bases and current_frozen
        any_frozen_base = any_frozen_base or current_frozen

    if has_dataclass_bases:
        if any_frozen_base and not frozen:
            raise TypeError('cannot inherit non-frozen dataclass from a frozen one')

        if all_frozen_bases is False and frozen:
            raise TypeError('cannot inherit frozen dataclass from a non-frozen one')


##


@dc.dataclass(frozen=True)
class FrozenPlan(Plan):
    fields: tuple[str, ...]


@register_generator_type(FrozenPlan)
class FrozenGenerator(Generator[FrozenPlan]):
    def plan(self, ctx: PlanContext) -> PlanResult[FrozenPlan] | None:
        check_frozen_bases(ctx.cls, ctx.cs.frozen)

        if not ctx.cs.frozen:
            return None

        return PlanResult(FrozenPlan(tuple(f.name for f in ctx.cs.fields)))

    def generate(self, pl: FrozenPlan) -> ta.Iterable[Op]:
        # https://github.com/python/cpython/commit/ee6f8413a99d0ee4828e1c81911e203d3fff85d5
        condition = f'type(self) is {CLS_IDENT}'
        if pl.fields:
            condition += ' or name in {' + ', '.join(repr(f) for f in pl.fields) + '}'

        return [
            AddMethodOp(
                name='__setattr__',
                src='\n'.join([
                    f'def __setattr__(self, name, value):',
                    f'    if {condition}:',
                    f'        raise {FROZEN_INSTANCE_ERROR_IDENT}',
                    f'    super({CLS_IDENT}, self).__setattr__(name, value)',
                ]),
            ),

            AddMethodOp(
                name='__delattr__',
                src='\n'.join([
                    f'def __delattr__(self, name):',
                    f'    if {condition}:',
                    f'        raise {FROZEN_INSTANCE_ERROR_IDENT}',
                    f'    super({CLS_IDENT}, self).__delattr__(name)',
                ]),
            ),
        ]
