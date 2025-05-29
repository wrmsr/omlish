import collections.abc
import io
import typing as ta

from omlish import dispatch

from .content import Content


##


class StringRenderer:
    def __init__(self, out: ta.TextIO) -> None:
        super().__init__()

        self._out = out

    @dispatch.method
    def render(self, c: Content) -> None:
        raise TypeError(c)

    @render.register
    def render_str(self, c: str) -> None:
        self._out.write(c)

    @render.register
    def render_sequence(self, s: collections.abc.Sequence) -> None:
        for e in s:
            self.render(e)

    @classmethod
    def render_to_str(cls, c: Content) -> str:
        out = io.StringIO()
        cls(out).render(c)
        return out.getvalue()
