"""
check.is_(check.isinstance(cls.__dict__[PARAMS_ATTR], Params), info.params)
check.is_(check.isinstance(check.not_none(info.cls_metadata)[ParamsExtras], ParamsExtras), info.params_extras)  # noqa

    def _check_params(self) -> None:
        if self._info.params.order and not self._info.params.eq:
            raise ValueError('eq must be true if order is true')

"""
from omlish import check

from ..processing.base import ProcessingContext
from ..processing.base import Processor
from ..processing.registry import register_processor_type
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processing_context_item_factory
from ..std.conversion import class_spec_to_spec_std_params
from ..std.internals import STD_PARAMS_ATTR
from ..std.internals import StdParams


##


@register_processing_context_item_factory(StdParams)
def _std_params_processing_context_item_factory(ctx: ProcessingContext) -> StdParams:
    return class_spec_to_spec_std_params(ctx.cs)


##


@register_processor_type(priority=ProcessorPriority.BOOTSTRAP)
class ParamsProcessor(Processor):
    def check(self) -> None:
        check.not_in(STD_PARAMS_ATTR, self._ctx.cls.__dict__)
        check.not_none(self._ctx[StdParams])

    def process(self, cls: type) -> type:
        setattr(cls, STD_PARAMS_ATTR, self._ctx[StdParams])

        return cls
