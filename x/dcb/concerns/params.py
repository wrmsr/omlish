from omlish import check

from ..processing.base import Processor
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processor_type
from ..std.internals import STD_PARAMS_ATTR


##


@register_processor_type(priority=ProcessorPriority.BOOTSTRAP)
class ParamsProcessor(Processor):
    def check(self) -> None:
        check.in_(STD_PARAMS_ATTR, self._ctx.cls.__dict__)
