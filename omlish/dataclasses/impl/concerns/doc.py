import inspect
import sys

from ..processing.base import ProcessingContext
from ..processing.base import Processor
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processor_type


##


if sys.version_info >= (3, 14):
    import annotationlib  # noqa

    def _raw_build_cls_sig(cls: type) -> str:
        return str(inspect.signature(
            cls,
            annotation_format=annotationlib.Format.FORWARDREF,  # noqa
        )).replace(' -> None', '')

else:
    def _raw_build_cls_sig(cls: type) -> str:
        return str(inspect.signature(cls)).replace(' -> None', '')


def _build_cls_doc(cls: type) -> str:
    try:
        text_sig = _raw_build_cls_sig(cls)
    except (TypeError, ValueError):
        text_sig = ''
    return cls.__name__ + text_sig


##


class _LazyClsDocDescriptor:
    def __get__(self, instance, owner=None):
        if instance is not None:
            owner = instance.__class__
        if not owner:
            raise RuntimeError
        doc = _build_cls_doc(owner)
        owner.__doc__ = doc
        return doc


@register_processor_type(priority=ProcessorPriority.POST_GENERATION)
class DocProcessor(Processor):
    def __init__(
            self,
            ctx: ProcessingContext,
            *,
            lazy: bool = True,
    ) -> None:
        super().__init__(ctx)

        self._lazy = lazy

    def process(self, cls: type) -> type:
        # FIXME: doesn't update doc in subclasses lol, as per stdlib
        if getattr(cls, '__doc__'):
            return cls

        if self._lazy:
            cls.__doc__ = _LazyClsDocDescriptor()  # type: ignore
        else:
            cls.__doc__ = _build_cls_doc(cls)

        return cls
