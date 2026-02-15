from .... import check
from ..._internals import STD_PARAMS_ATTR
from ..processing.base import Processor
from ..processing.phases import ProcessorPhase
from ..processing.registry import register_processor_type


##


@register_processor_type(phase=ProcessorPhase.BOOTSTRAP)
class ParamsProcessor(Processor):
    def check(self) -> None:
        check.in_(STD_PARAMS_ATTR, self._ctx.cls.__dict__)
