from omlish import check
from omlish import lang

from .base import Generator
from .base import Plan


##


_GENERATOR_TYPES_BY_BLUEPRINT_TYPES_SEALED = False
_GENERATOR_TYPES_BY_BLUEPRINT_TYPE: dict[type[Plan], type[Generator]] = {}


def _seal_registry() -> None:
    global _GENERATOR_TYPES_BY_BLUEPRINT_TYPES_SEALED
    if not _GENERATOR_TYPES_BY_BLUEPRINT_TYPES_SEALED:
        _GENERATOR_TYPES_BY_BLUEPRINT_TYPES_SEALED = True


def register_generator_type(pl_ty):
    def inner(g_ty):
        check.state(not _GENERATOR_TYPES_BY_BLUEPRINT_TYPES_SEALED)
        check.issubclass(g_ty, Generator)
        check.not_in(pl_ty, _GENERATOR_TYPES_BY_BLUEPRINT_TYPE)
        _GENERATOR_TYPES_BY_BLUEPRINT_TYPE[pl_ty] = g_ty
        return g_ty

    check.issubclass(pl_ty, Plan)
    return inner


@lang.cached_function
def generator_type_for_plan_type(pl_ty: type[Plan]) -> type[Generator]:
    _seal_registry()
    return _GENERATOR_TYPES_BY_BLUEPRINT_TYPE[pl_ty]


@lang.cached_function
def all_generator_types() -> tuple[type[Generator], ...]:
    _seal_registry()
    return tuple(sorted(set(
        _GENERATOR_TYPES_BY_BLUEPRINT_TYPE.values()),
        key=lambda g_ty: g_ty.__name__,
    ))
