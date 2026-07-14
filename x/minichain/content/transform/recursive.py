from ..content import Content
from .types import ContentTransform


##


class RecursiveContentTransformDepthExceededError(Exception):
    pass


class RecursiveContentTransform(ContentTransform):
    DEFAULT_MAX_ITERATIONS: int = 8

    def __init__(
            self,
            *children: ContentTransform,
            max_iterations: int = DEFAULT_MAX_ITERATIONS,
            debug: bool = False,
    ) -> None:
        super().__init__()

        self._children = children
        self._max_iterations = max_iterations
        self._debug = debug

    def transform(self, content: Content) -> Content:
        n = 0

        history: list[Content] | None = None
        if self._debug:
            history = []

        while True:
            if history is not None:
                history.append(content)

            if n >= self._max_iterations:
                raise RecursiveContentTransformDepthExceededError

            out = content
            for child in self._children:
                out = child.transform(out)

            if out is content:
                return content

            content = out
            n += 1
