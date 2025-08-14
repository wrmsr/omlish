"""
TODO:
 - prebuild field frozenset for getters/setters
  - and one field per line
"""
import dataclasses as dc
import typing as ta
import weakref

from .... import check
from ..._internals import STD_FIELDS_ATTR
from ..._internals import STD_PARAMS_ATTR
from ..generation.base import Generator
from ..generation.base import Plan
from ..generation.base import PlanResult
from ..generation.globals import FROZEN_INSTANCE_ERROR_GLOBAL
from ..generation.idents import CLS_IDENT
from ..generation.idents import IDENT_PREFIX
from ..generation.ops import AddMethodOp
from ..generation.ops import Op
from ..generation.registry import register_generator_type
from ..processing.base import ProcessingContext


##


_UNCHECKED_FROZEN_BASES: ta.MutableSet[type] = weakref.WeakSet()


def unchecked_frozen_base(cls):
    _UNCHECKED_FROZEN_BASES.add(check.isinstance(cls, type))
    return cls


def check_frozen_bases(cls: type, frozen: bool) -> None:
    all_frozen_bases = None
    any_frozen_base = False
    has_dataclass_bases = False

    for b in cls.__mro__[-1:0:-1]:
        if b in _UNCHECKED_FROZEN_BASES:
            continue

        base_fields = getattr(b, STD_FIELDS_ATTR, None)
        if base_fields is None:
            continue

        has_dataclass_bases = True
        if all_frozen_bases is None:
            all_frozen_bases = True

        current_frozen = getattr(b, STD_PARAMS_ATTR).frozen
        all_frozen_bases = all_frozen_bases and current_frozen
        any_frozen_base = any_frozen_base or current_frozen

    if has_dataclass_bases:
        if any_frozen_base and not frozen:
            raise TypeError('cannot inherit non-frozen dataclass from a frozen one')

        if all_frozen_bases is False and frozen:
            raise TypeError('cannot inherit frozen dataclass from a non-frozen one')


##


@dc.dataclass(frozen=True, kw_only=True)
class FrozenPlan(Plan):
    fields: tuple[str, ...]
    allow_dynamic_dunder_attrs: bool


@register_generator_type(FrozenPlan)
class FrozenGenerator(Generator[FrozenPlan]):
    def plan(self, ctx: ProcessingContext) -> PlanResult[FrozenPlan] | None:
        check_frozen_bases(ctx.cls, ctx.cs.frozen)

        if not ctx.cs.frozen:
            return None

        return PlanResult(FrozenPlan(
            fields=tuple(f.name for f in ctx.cs.fields),
            allow_dynamic_dunder_attrs=ctx.cs.allow_dynamic_dunder_attrs,
        ))

    def _generate_one(
            self,
            plan: FrozenPlan,
            mth: str,
            params: ta.Sequence[str],
            exc_args: str,
    ) -> AddMethodOp:
        preamble = []
        condition = []

        # https://github.com/python/cpython/commit/ee6f8413a99d0ee4828e1c81911e203d3fff85d5
        base_condition = f'type(self) is {CLS_IDENT}'

        if plan.allow_dynamic_dunder_attrs:
            condition.extend([
                f'(',
                f'    {base_condition}',
                f'    and not (len(name) > 4 and name[:2] == name[-2:] == "__")',
                f')',
            ])
        else:
            condition.append(base_condition)

        if plan.fields:
            set_ident = f'{IDENT_PREFIX}_{mth}_frozen_fields'
            preamble.extend([
                f'{set_ident} = {{',
                *[
                    f'    {f!r},'
                    for f in plan.fields
                ],
                f'}}',
                f'',
            ])
            condition.append(f' or name in {set_ident}')

        return AddMethodOp(
            f'__{mth}__',
            '\n'.join([
                *preamble,
                f'def __{mth}__(self, {", ".join(params)}):',
                f'    if (',
                *[
                    f'        {l}'
                    for l in condition
                ],
                f'    ):',
                f'        raise {FROZEN_INSTANCE_ERROR_GLOBAL.ident}{exc_args}',
                f'    super({CLS_IDENT}, self).__{mth}__({", ".join(params)})',
            ]),
            frozenset([FROZEN_INSTANCE_ERROR_GLOBAL]),
        )

    def generate(self, plan: FrozenPlan) -> ta.Iterable[Op]:
        return [
            self._generate_one(
                plan,
                'setattr',
                ['name', 'value'],
                '(f"cannot assign to field {name!r}")',
            ),
            self._generate_one(
                plan,
                'delattr',
                ['name'],
                '(f"cannot delete field {name!r}")',
            ),
        ]
