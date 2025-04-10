from omlish import lang

from .generation.processor import GeneratorProcessor
from .processing import ProcessingContext
from .registry import all_context_item_factories
from .specs import CLASS_SPEC_ATTR
from .specs import ClassSpec


##


@lang.cached_function
def _import_concerns() -> None:
    from . import concerns  # noqa


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

    GeneratorProcessor(ctx).process()

    return cls
