from . import concerns as _ # noqa
from .generation import processor as _  # noqa
from .processing.registry import ordered_processor_types
from .processing.base import Processor
from .processing.base import ProcessingContext
from .processing.registry import all_processing_context_item_factories
from .specs import ClassSpec


##


def drive_cls_processing(
        cls: type,
        cs: ClassSpec,
) -> type:
    ctx = ProcessingContext(
        cls,
        cs,
        all_processing_context_item_factories(),
    )

    processors: list[Processor] = [
        proc_cls(ctx)
        for proc_cls in ordered_processor_types()
    ]

    for p in processors:
        p.check()

    ret = cls
    for p in processors:
        ret = p.process(ret)

    return ret
