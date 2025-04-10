from omlish import check

from ..processing.base import ProcessingContext
from ..processing.base import Processor
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processing_context_item_factory
from ..processing.registry import register_processor_type
from ..std.conversion import class_spec_to_std_params
from ..std.internals import STD_PARAMS_ATTR
from ..std.internals import StdParams


##


@register_processing_context_item_factory(StdParams)
def _std_params_processing_context_item_factory(ctx: ProcessingContext) -> StdParams:
    return class_spec_to_std_params(ctx.cs, use_spec_wrapper=True)


##


@register_processor_type(priority=ProcessorPriority.BOOTSTRAP)
class ParamsProcessor(Processor):
    def check(self) -> None:
        check.not_in(STD_PARAMS_ATTR, self._ctx.cls.__dict__)
        check.not_none(self._ctx[StdParams])

    def process(self, cls: type) -> type:
        setattr(cls, STD_PARAMS_ATTR, self._ctx[StdParams])
        return cls
