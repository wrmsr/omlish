import collections.abc
import typing as ta

from omlish import lang

from ..metadata import ContentOriginal
from ..sequence import BlockContent
from ..sequence import InlineContent
from ..sequence import SequenceContent
from ..text import TextContent
from .base import Content
from .base import ContentTransform


##


class StandardContentTransformTypeError(TypeError):
    pass


class StandardContentTransform(ContentTransform, lang.Abstract):
    @ContentTransform.apply.register
    def apply_str(self, s: str) -> str:
        raise StandardContentTransformTypeError(s)

    @ContentTransform.apply.register
    def apply_sequence(self, l: collections.abc.Sequence) -> collections.abc.Sequence:
        raise StandardContentTransformTypeError(l)


##


class LiftToStandardContentTransform(ContentTransform):
    def __init__(
            self,
            *,
            sequence_mode: ta.Literal['block', 'inline'] = 'block',
    ) -> None:
        super().__init__()

        self._sequence_mode = sequence_mode

    @ContentTransform.apply.register
    def apply_str(self, s: str) -> Content:
        return TextContent(s).update_metadata(ContentOriginal(s))

    @ContentTransform.apply.register
    def apply_sequence(self, l: collections.abc.Sequence) -> Content:
        c: SequenceContent
        match self._sequence_mode:
            case 'block':
                c = BlockContent(l)
            case 'inline':
                c = InlineContent(l)
            case _:
                raise ValueError(self._sequence_mode)
        return c.update_metadata(ContentOriginal(l))
