import functools
import typing as ta

from omlish import check

from ..... import minichain as mc
from ....content.messages import MessageContentExtractor
from ....content.messages import MessageContentExtractorImpl
from ....interfaces.bare.printing.types import ContentPrinting
from ....interfaces.bare.printing.types import StreamContentPrinting


##


class AiMessagesEventPrinter:
    def __init__(
            self,
            *,
            extractor: MessageContentExtractor | None = None,
            printer: ContentPrinting,
    ) -> None:
        super().__init__()

        if extractor is None:
            extractor = MessageContentExtractorImpl()
        self._extractor = extractor
        self._printer = printer

    async def handle_event(self, event: mc.drivers.Event) -> None:
        if isinstance(event, mc.drivers.AiMessagesEvent):
            for msg in event.chat:
                if (c := self._extractor.extract_message_content(msg)) is not None:
                    await self._printer.print_content(c)


class AiDeltaEventPrinter:
    def __init__(
            self,
            *,
            extractor: MessageContentExtractor | None = None,
            printer: StreamContentPrinting,
    ) -> None:
        super().__init__()

        if extractor is None:
            extractor = MessageContentExtractorImpl()
        self._extractor = extractor
        self._printer = printer

        self._print_ctx: ContentPrinting | None = None
        self._close_print_ctx: ta.Callable[[], ta.Awaitable[ta.Any]] | None = None

    async def handle_event(self, event: mc.drivers.Event) -> None:
        if isinstance(event, mc.drivers.AiStreamBeginEvent):
            check.none(self._print_ctx)
            check.none(self._close_print_ctx)
            acm = self._printer.create_context()
            self._print_ctx = await acm.__aenter__()
            self._close_print_ctx = functools.partial(acm.__aexit__, None, None, None)

        elif isinstance(event, mc.drivers.AiStreamDeltaEvent):
            if isinstance(event.delta, mc.ContentAiDelta):
                await check.not_none(self._print_ctx).print_content(event.delta.c)

        elif isinstance(event, mc.drivers.AiStreamEndEvent):
            check.not_none(self._print_ctx)
            await (check.not_none(self._close_print_ctx)())
            self._print_ctx = None
            self._close_print_ctx = None


##


class ToolUseEventsPrinter:
    def __init__(
            self,
            *,
            printer: ContentPrinting,
    ) -> None:
        super().__init__()

        self._printer = printer

    async def handle_event(self, event: mc.drivers.Event) -> None:
        if isinstance(event, mc.drivers.ToolUseEvent):
            await self._printer.print_content(mc.JsonContent(dict(
                id=event.use.id,
                name=event.use.name,
                args=event.use.args,
            )))

        elif isinstance(event, mc.drivers.ToolUseResultEvent):
            await self._printer.print_content(event.message.tur.c)
