import typing as ta

from omlish import lang

from .generation.processor import GeneratorProcessor
from .processing import ProcessingContext
from .processing import Processor
from .registry import all_context_item_factories
from .specs import CLASS_SPEC_ATTR
from .specs import ClassSpec


##


@lang.cached_function
def _import_concerns() -> None:
    from . import concerns  # noqa


PROCESSOR_TYPES: ta.Sequence[type[Processor]] = [
    GeneratorProcessor,
]


def drive_cls_processing(
        cls: type,
        cs: ClassSpec,
) -> type:
    _import_concerns()

    setattr(cls, CLASS_SPEC_ATTR, cs)

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
