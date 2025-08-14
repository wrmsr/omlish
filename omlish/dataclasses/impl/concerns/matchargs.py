from .... import check
from ..processing.base import Processor
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processor_type
from ..utils import set_new_attribute
from .fields import InitFields


##


@register_processor_type(priority=ProcessorPriority.POST_GENERATION)
class MatchArgsProcessor(Processor):
    def check(self) -> None:
        check.not_none(self._ctx[InitFields])

    def process(self, cls: type) -> type:
        if not self._ctx.cs.match_args or '__match_args__' in self._ctx.cls.__dict__:
            return cls

        set_new_attribute(
            cls,
            '__match_args__',
            tuple(f.name for f in self._ctx[InitFields].std),
        )

        return cls
