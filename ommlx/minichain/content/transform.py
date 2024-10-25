import collections.abc

from omlish import dispatch

from .content import Content
from .images import Image
from .placeholders import Env
from .placeholders import Placeholder


##


class PlaceholderTransform:
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
    def apply_placeholder(self, c: Placeholder) -> Placeholder:
        raise NotImplementedError
