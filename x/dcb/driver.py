import typing as ta

from . import concerns  # noqa
from .concerns.doc import DocProcessor
from .concerns.fields import FieldsProcessor
from .concerns.replace import ReplaceProcessor
from .concerns.slots import SlotsProcessor
from .generation.processor import GeneratorProcessor
from .processing import ProcessingContext
from .processing import Processor
from .registry import all_context_item_factories
from .specs import ClassSpec


##


PROCESSOR_TYPES: ta.Sequence[type[Processor]] = [
    FieldsProcessor,
    GeneratorProcessor,
    ReplaceProcessor,
    DocProcessor,
    SlotsProcessor,
]


def drive_cls_processing(
        cls: type,
        cs: ClassSpec,
) -> type:
    # setattr(cls, CLASS_SPEC_ATTR, cs)

    ctx = ProcessingContext(
        cls,
        cs,
        all_context_item_factories(),
    )

    processors: list[Processor] = [
        proc_cls(ctx)
        for proc_cls in PROCESSOR_TYPES
    ]

    for p in processors:
        p.check()

    ret = cls
    for p in processors:
        ret = p.process(ret)

    return ret
