# ruff: noqa: SLF001
import typing as ta
import uuid

from omdev import clipboard as cpb
from omdev.tui import textual as tx
from omlish import check
from omlish import lang
from omlish.asyncs.relays import SchedulingAsyncBufferRelay

from .base import Message
from .stream import ContentStreamMessagePart
from .stream import FinalStreamMessagePart
from .stream import StreamMessage
from .stream import StreamMessagePart


##


class MessagesContainer(
    tx.InitAddClass,
    tx.ComposeOnce,
    tx.VerticalScroll,
):
    init_add_class = 'messages-container'

    def __init__(
            self,
            clipboard: cpb.Clipboard | None = None,
            chat_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__()

        self._clipboard = clipboard
        self._chat_uuid = chat_uuid

        self._messages_by_uuid: dict[uuid.UUID, Message] = {}

        self._mount_message_buffer: SchedulingAsyncBufferRelay[Message] = SchedulingAsyncBufferRelay(  # noqa
            lang.as_async(lambda: self.call_next(self._drain_mount_message_buffer)),
        )
        self._scroll_to_bottom_after_mount_messages = False
        self._refresh_after_mount_messages = False

    @property
    def chat_uuid(self) -> uuid.UUID | None:
        return self._chat_uuid

    #

    def _compose_once(self) -> tx.ComposeResult:
        return
        yield  # noqa

    #

    def _is_messages_at_bottom(self, threshold: int = 3) -> bool:
        return self.scroll_y >= (self.max_scroll_y - threshold)

    def _anchor_messages(self) -> None:
        if self.max_scroll_y:
            self.anchor()

    #

    async def append_stream_message_content(self, parts: ta.Sequence[StreamMessagePart]) -> None:
        for part in parts:
            if isinstance(part, ContentStreamMessagePart):
                message_uuid = part.message_uuid
                content = part.content

                if (msg := self._messages_by_uuid.get(message_uuid)) is None:
                    aim = part.message_cls(content, message_uuid=message_uuid)

                    self._messages_by_uuid[message_uuid] = aim

                    await self.mount_messages(aim)
                    self._refresh_after_mount_messages = True

                else:
                    aim = check.isinstance(msg, part.message_cls)

                    if aim.is_mounted:
                        self._scroll_to_bottom_after_mount_messages |= self._is_messages_at_bottom()

                    await aim.append_stream_content(content)

            elif isinstance(part, FinalStreamMessagePart):
                if (msg := self._messages_by_uuid.get(part.message_uuid)) is None:
                    continue

                aim = check.isinstance(msg, part.message_cls)

                await aim.finalize_stream()

            else:
                raise TypeError(part)

    #

    async def mount_messages(self, *messages: Message) -> None:
        await self._mount_messages(*messages)

    async def _drain_mount_message_buffer(self) -> None:
        messages = await self._mount_message_buffer.swap()
        await self._mount_messages(*messages)

    async def _mount_messages(self, *messages: Message) -> None:
        was_at_bottom = self._is_messages_at_bottom()

        for msg in messages:
            if (mu := msg.message_uuid) is not None:
                try:
                    xm = self._messages_by_uuid[mu]
                except KeyError:
                    pass
                else:
                    if not (isinstance(msg, StreamMessage) and xm is msg):
                        raise ValueError(f'message uuid already in use: {mu}')

            await self.mount(msg)

            if mu is not None:
                self._messages_by_uuid[mu] = msg

            if isinstance(msg, StreamMessage):
                await msg.start_stream()

        if was_at_bottom or self._scroll_to_bottom_after_mount_messages:
            self._scroll_to_bottom_after_mount_messages = False
            self.call_after_refresh(self._anchor_messages)

        if self._refresh_after_mount_messages:
            self._refresh_after_mount_messages = False
            self.refresh()
