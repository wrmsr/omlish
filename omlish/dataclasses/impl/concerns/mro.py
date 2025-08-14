import typing as ta

from .... import lang
from ..processing.base import ProcessingContext
from ..processing.registry import register_processing_context_item_factory


##


MroDict = ta.NewType('MroDict', ta.Mapping[str, ta.Any])


@register_processing_context_item_factory(MroDict)
def _mro_dict_processing_context_item_factory(ctx: ProcessingContext) -> MroDict:
    return MroDict(lang.mro_dict(ctx.cls))
