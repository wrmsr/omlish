import collections.abc
import io
import typing as ta

from omlish import dispatch

from .content import Content
from .images import Image
from .placeholders import Env
from .placeholders import Placeholder


##


class PlaceholderFiller:
    def __init__(self, env: Env) -> None:
        super().__init__()
        self._env = env

    @dispatch.method
    def apply(self, c: Content) -> Content:
        raise TypeError(c)

    @apply.register
    def apply_str(self, c: str) -> str:
        return c

    @apply.register
    def apply_sequence(self, s: collections.abc.Sequence) -> collections.abc.Sequence:
        return [self.apply(e) for e in s]

    @apply.register
    def apply_image(self, c: Image) -> Image:
        return c

    @apply.register
    def apply_placeholder(self, c: Placeholder) -> str:
        return self._env[c.k]


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
