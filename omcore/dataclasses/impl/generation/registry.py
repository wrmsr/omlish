import typing as ta

from .... import check
from .... import lang
from ..utils import SealableRegistry
from .base import Generator
from .base import Plan


K = ta.TypeVar('K')
V = ta.TypeVar('V')

GeneratorT = ta.TypeVar('GeneratorT', bound=Generator)


##


_GENERATOR_TYPES_BY_PLAN_TYPE: SealableRegistry[type[Plan], type[Generator]] = SealableRegistry()


def register_generator_type(pl_ty: type[Plan]) -> ta.Callable[[type[GeneratorT]], type[GeneratorT]]:
    def inner(g_ty):
        check.issubclass(g_ty, Generator)
        _GENERATOR_TYPES_BY_PLAN_TYPE[pl_ty] = g_ty
        return g_ty

    check.issubclass(pl_ty, Plan)
    return inner


@lang.cached_function
def generator_type_for_plan_type(pl_ty: type[Plan]) -> type[Generator]:
    return _GENERATOR_TYPES_BY_PLAN_TYPE[pl_ty]


@lang.cached_function
def all_generator_types() -> tuple[type[Generator], ...]:
    return tuple(sorted(
        {v for _, v in _GENERATOR_TYPES_BY_PLAN_TYPE.items()},
        key=lambda g_ty: g_ty.__name__,
    ))
