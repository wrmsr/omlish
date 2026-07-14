import abc

from ..processing.base import Processor
from ..processing.phases import ProcessorPhase
from ..processing.registry import register_processor_type


##


@register_processor_type(phase=ProcessorPhase.POST_SLOTS)
class UpdateAbstractMethodsProcessor(Processor):
    def process(self, cls: type) -> type:
        abc.update_abstractmethods(cls)  # noqa
        return cls
