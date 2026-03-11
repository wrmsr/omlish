import typing as ta

from omlish import lang

from ..... import minichain as mc
from ....content.strings import ContentStringifier
from ....content.strings import HasContentStringifier
from .types import ContentPrinting
from .types import StreamContentPrinting


##


class RawContentPrinting(ContentPrinting, HasContentStringifier):
    def __init__(
            self,
            *,
            printer: ta.Callable[[str], ta.Awaitable[None]] | None = None,
            content_stringifier: ContentStringifier | None = None,
    ) -> None:
        super().__init__(content_stringifier=content_stringifier)

        if printer is None:
            printer = lang.as_async(print)
        self._printer = printer

    async def print_content(self, content: 'mc.Content') -> None:
        if (s := self._content_stringifier.stringify_content(content)) is not None:
            await self._printer(s)


class RawStreamContentPrinting(StreamContentPrinting, HasContentStringifier):
    class Output(ta.Protocol):
        def write(self, s: str) -> ta.Awaitable[None]: ...
        def flush(self) -> ta.Awaitable[None]: ...

    class PrintOutput:
        async def write(self, s: str) -> None:
            print(s, end='', flush=True)

        async def flush(self) -> None:
            print(flush=True)

    def __init__(
            self,
            *,
            output: Output | None = None,
            content_stringifier: ContentStringifier | None = None,
    ) -> None:
        super().__init__(content_stringifier=content_stringifier)

        if output is None:
            output = RawStreamContentPrinting.PrintOutput()
        self._output = output

    @ta.final
    class _ContextInstance(ContentPrinting, ta.AsyncContextManager):
        def __init__(self, owner: 'RawStreamContentPrinting') -> None:
            self._owner = owner

        async def __aenter__(self) -> ta.Self:
            return self

        async def __aexit__(self, *exc_info) -> None:
            await self._owner._output.flush()  # noqa: SLF001

        async def print_content(self, content: 'mc.Content') -> None:
            if (s := self._owner._content_stringifier.stringify_content(content)) is not None:  # noqa: SLF001
                await self._owner._output.write(s)  # noqa: SLF001

    def create_context(self) -> ta.AsyncContextManager[ContentPrinting]:
        return RawStreamContentPrinting._ContextInstance(self)
