from .. import concerns as _concerns # noqa
from ..generation import processor as _generation_processor  # noqa
from ..specs import ClassSpec
from .base import ProcessingContext
from .base import Processor
from .registry import all_processing_context_item_factories
from .registry import ordered_processor_types


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
