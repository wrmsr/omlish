import abc

from ..processing.base import Processor
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processor_type


##


@register_processor_type(priority=ProcessorPriority.POST_SLOTS)
class UpdateAbstractMethodsProcessor(Processor):
    def process(self, cls: type) -> type:
        abc.update_abstractmethods(cls)  # noqa
        return cls
