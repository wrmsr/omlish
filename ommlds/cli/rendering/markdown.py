import typing as ta

from omdev.tui import rich
from omlish import lang

from ... import minichain as mc
from ..content.strings import ContentStringifier
from ..content.strings import HasContentStringifier
from .types import ContentRendering
from .types import StreamContentRendering


##


class MarkdownContentRendering(ContentRendering, HasContentStringifier):
    def __init__(
            self,
            *,
            content_stringifier: ContentStringifier | None = None,
    ) -> None:
        super().__init__(content_stringifier=content_stringifier)

    async def render_content(self, content: 'mc.Content') -> None:
        if (s := self._content_stringifier.stringify_content(content)) is not None and (s := s.strip()):
            rich.Console().print(rich.Markdown(s))


class MarkdownStreamContentRendering(StreamContentRendering, HasContentStringifier):
    def __init__(
            self,
            *,
            content_stringifier: ContentStringifier | None = None,
    ) -> None:
        super().__init__(content_stringifier=content_stringifier)

    @ta.final
    class _ContextInstance(ContentRendering, lang.AsyncExitStacked):
        def __init__(self, owner: 'MarkdownStreamContentRendering') -> None:
            self._owner = owner

        _ir: rich.MarkdownLiveStream

        async def _async_enter_contexts(self) -> None:
            self._ir = self._enter_context(rich.IncrementalMarkdownLiveStream())

        async def render_content(self, content: 'mc.Content') -> None:
            if (s := self._owner._content_stringifier.stringify_content(content)) is not None:  # noqa: SLF001
                self._ir.feed(s)

    def create_context(self) -> ta.AsyncContextManager[ContentRendering]:
        return MarkdownStreamContentRendering._ContextInstance(self)
