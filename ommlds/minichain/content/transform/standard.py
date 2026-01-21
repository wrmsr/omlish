import collections.abc
import typing as ta

from omlish import check

from ..content import Content
from ..metadata import ContentOriginal
from ..sequence import BlockContent
from ..sequence import InlineContent
from ..sequence import SequenceContent
from ..text import TextContent
from .visitors import VisitorContentTransform


##


class LiftToStandardContentTransform(VisitorContentTransform[None]):
    def __init__(
            self,
            *,
            sequence_mode: ta.Literal['block', 'inline'] = 'block',
    ) -> None:
        super().__init__()

        self._sequence_mode = sequence_mode

    def visit_str(self, s: str, ctx: None) -> Content:
        return TextContent(s).with_metadata(ContentOriginal(s))

    def visit_sequence(self, c: ta.Sequence[Content], ctx: None) -> Content:
        cc = check.isinstance(super().visit_sequence(c, ctx), collections.abc.Sequence)

        nc: SequenceContent
        match self._sequence_mode:
            case 'block':
                nc = BlockContent(cc)
            case 'inline':
                nc = InlineContent(cc)
            case _:
                raise ValueError(self._sequence_mode)

        return nc.with_metadata(ContentOriginal(c))
