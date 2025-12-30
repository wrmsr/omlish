import typing as ta

from ..content import Content
from ..metadata import ContentOriginal
from ..sequence import BlockContent
from ..sequence import InlineContent
from ..sequence import SequenceContent
from ..text import TextContent
from ..visitors import ContentTransform


##


class LiftToStandardContentTransform(ContentTransform[None]):
    def __init__(
            self,
            *,
            sequence_mode: ta.Literal['block', 'inline'] = 'block',
    ) -> None:
        super().__init__()

        self._sequence_mode = sequence_mode

    def visit_str(self, s: str, ctx: None) -> Content:
        return TextContent(s).update_metadata(ContentOriginal(s))

    def visit_sequence(self, c: ta.Sequence[Content], ctx: None) -> Content:
        cc = super().visit_sequence(c, ctx)

        c: SequenceContent
        match self._sequence_mode:
            case 'block':
                c = BlockContent(cc)
            case 'inline':
                c = InlineContent(cc)
            case _:
                raise ValueError(self._sequence_mode)

        return c.update_metadata(ContentOriginal(c))
