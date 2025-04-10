import typing as ta

from omlish import check
from omlish import lang

from .base import Generator
from .base import Plan


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class _SealableRegistry(ta.Generic[K, V]):
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[K, V] = {}
        self._sealed = False

    def seal(self) -> None:
        self._sealed = True

    def __setitem__(self, k: K, v: V) -> None:
        check.state(not self._sealed)
        check.not_in(k, self._dct)
        self._dct[k] = v

    def __getitem__(self, k: K) -> V:
        self.seal()
        return self._dct[k]

    def items(self) -> ta.Iterator[tuple[K, V]]:
        self.seal()
        return iter(self._dct.items())


##


_GENERATOR_TYPES_BY_PLAN_TYPE: _SealableRegistry[type[Plan], type[Generator]] = _SealableRegistry()


def register_generator_type(pl_ty):
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


##


_CONTEXT_ITEM_FACTORIES: _SealableRegistry[type, ta.Callable] = _SealableRegistry()


def register_context_item_factory(i_ty):
    def inner(fn):
        _CONTEXT_ITEM_FACTORIES[i_ty] = fn
        return fn

    return inner


@lang.cached_function
def context_item_factory_for(i_ty: type) -> ta.Callable:
    return _CONTEXT_ITEM_FACTORIES[i_ty]


@lang.cached_function
def all_context_factories() -> ta.Mapping[type, ta.Callable]:
    return dict(_CONTEXT_ITEM_FACTORIES.items())
