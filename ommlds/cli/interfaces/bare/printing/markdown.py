import typing as ta

from omdev.tui import rich
from omdev.tui.rich import textual as rich_tx
from omlish import lang

from ..... import minichain as mc
from ....content.strings import ContentStringifier
from ....content.strings import HasContentStringifier
from .types import ContentPrinting
from .types import StreamContentPrinting


##


class RichMarkdown(ta.NamedTuple):
    theme: ta.Any
    code_theme: ta.Any


@lang.cached_function
def rich_markdown() -> RichMarkdown:
    return RichMarkdown(
        rich_tx.build_theme(rich_tx.TEXTUAL_DARK),
        rich_tx.build_pygments_theme(rich_tx.TEXTUAL_DARK),
    )


##


class MarkdownContentPrinting(ContentPrinting, HasContentStringifier):
    def __init__(
            self,
            *,
            content_stringifier: ContentStringifier | None = None,
    ) -> None:
        super().__init__(content_stringifier=content_stringifier)

    async def print_content(self, content: mc.Content) -> None:
        rm = rich_markdown()
        if (s := self._content_stringifier.stringify_content(content)) is not None and (s := s.strip()):
            rich.Console(theme=rm.theme).print(rich.Markdown(s, code_theme=rm.code_theme))


class MarkdownStreamContentPrinting(StreamContentPrinting, HasContentStringifier):
    def __init__(
            self,
            *,
            content_stringifier: ContentStringifier | None = None,
    ) -> None:
        super().__init__(content_stringifier=content_stringifier)

    @ta.final
    class _ContextInstance(ContentPrinting, lang.AsyncExitStacked):
        def __init__(self, owner: MarkdownStreamContentPrinting) -> None:
            self._owner = owner

        _ir: rich.MarkdownLiveStream

        async def _async_enter_contexts(self) -> None:
            rm = rich_markdown()
            self._ir = self._enter_context(rich.IncrementalMarkdownLiveStream(
                render_console_kwargs=dict(theme=rm.theme),
                markdown_kwargs=dict(code_theme=rm.code_theme),
            ))

        async def print_content(self, content: mc.Content) -> None:
            if (s := self._owner._content_stringifier.stringify_content(content)) is not None:  # noqa: SLF001
                self._ir.feed(s)

    def create_context(self) -> ta.AsyncContextManager[ContentPrinting]:
        return MarkdownStreamContentPrinting._ContextInstance(self)
