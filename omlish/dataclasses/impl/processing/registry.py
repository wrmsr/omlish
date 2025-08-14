import dataclasses as dc
import typing as ta

from .... import check
from .... import lang
from ..utils import SealableRegistry
from .base import ProcessingContextItemFactory
from .base import Processor
from .priority import ProcessorPriority


ProcessorT = ta.TypeVar('ProcessorT', bound=Processor)


##


_PROCESSING_CONTEXT_ITEM_FACTORIES: SealableRegistry[type, ProcessingContextItemFactory] = SealableRegistry()


def register_processing_context_item_factory(i_ty):
    def inner(fn):
        _PROCESSING_CONTEXT_ITEM_FACTORIES[i_ty] = fn
        return fn

    return inner


@lang.cached_function
def processing_context_item_factory_for(i_ty: type) -> ProcessingContextItemFactory:
    return _PROCESSING_CONTEXT_ITEM_FACTORIES[i_ty]


@lang.cached_function
def all_processing_context_item_factories() -> ta.Mapping[type, ProcessingContextItemFactory]:
    return dict(_PROCESSING_CONTEXT_ITEM_FACTORIES.items())


##


@dc.dataclass(frozen=True, kw_only=True)
class ProcessorTypeRegistration:
    priority: ProcessorPriority


_PROCESSOR_TYPES: SealableRegistry[type[Processor], ProcessorTypeRegistration] = SealableRegistry()


def register_processor_type(
        *,
        priority: ProcessorPriority,
        **kwargs: ta.Any,
) -> ta.Callable[[type[ProcessorT]], type[ProcessorT]]:
    reg = ProcessorTypeRegistration(
        priority=priority,
        **kwargs,
    )

    def inner(ty):
        check.issubclass(ty, Processor)
        _PROCESSOR_TYPES[ty] = reg
        return ty

    return inner


@lang.cached_function
def all_processor_types() -> ta.Mapping[type, ProcessorTypeRegistration]:
    return dict(_PROCESSOR_TYPES.items())


@lang.cached_function
def ordered_processor_types() -> ta.Sequence[type]:
    return [
        t
        for t, r in sorted(
            all_processor_types().items(),
            key=lambda t_r: t_r[1].priority,
        )
    ]
