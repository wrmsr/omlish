import io
import typing as ta

from omlish import dispatch

from ..sequence import SequenceContent
from ..text import TextContent
from ..types import Content


##


class StringWriter(ta.Protocol):
    def write(self, s: str) -> ta.Any: ...


class ContentStringWriter:
    def __init__(
            self,
            out: StringWriter,
    ) -> None:
        super().__init__()

        self._out = out

    @dispatch.method()
    def write(self, c: Content) -> None:
        raise TypeError(c)

    #

    @write.register
    def write_str(self, c: str) -> None:
        self._out.write(c)

    @write.register
    def write_sequence(self, c: ta.Sequence) -> None:
        for e in c:
            self.write(e)

    #

    @write.register
    def write_text_content(self, c: TextContent) -> None:
        self._out.write(c.s)

    @write.register
    def write_sequence_content(self, c: SequenceContent) -> None:
        for e in c.l:
            self.write(e)

    #

    @classmethod
    def write_to_str(cls, c: Content, **kwargs: ta.Any) -> str:
        out = io.StringIO()
        cls(out, **kwargs).write(c)
        return out.getvalue()


def stringify_content(c: Content) -> str:
    return ContentStringWriter.write_to_str(c)
