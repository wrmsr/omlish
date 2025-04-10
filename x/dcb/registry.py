import typing as ta

from omlish import check
from omlish import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class SealableRegistry(ta.Generic[K, V]):
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


_PROCESSING_CONTEXT_ITEM_FACTORIES: SealableRegistry[type, ta.Callable] = SealableRegistry()


def register_processing_context_item_factory(i_ty):
    def inner(fn):
        _PROCESSING_CONTEXT_ITEM_FACTORIES[i_ty] = fn
        return fn

    return inner


@lang.cached_function
def processing_context_item_factory_for(i_ty: type) -> ta.Callable:
    return _PROCESSING_CONTEXT_ITEM_FACTORIES[i_ty]


@lang.cached_function
def all_processing_context_item_factories() -> ta.Mapping[type, ta.Callable]:
    return dict(_PROCESSING_CONTEXT_ITEM_FACTORIES.items())
