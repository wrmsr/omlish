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
        self._refresh_after_mount_messages = False

    @property
    def chat_uuid(self) -> uuid.UUID | None:
        return self._chat_uuid

    def get_message_by_uuid(self, message_uuid: uuid.UUID) -> Message | None:
        return self._messages_by_uuid.get(message_uuid)

    #

    def _compose_once(self) -> tx.ComposeResult:
        return
        yield  # noqa

    #

    def _is_messages_at_bottom(self, threshold: int = 3) -> bool:
        return self.scroll_y >= (self.max_scroll_y - threshold)

    def _scroll_messages_to_bottom(self) -> None:
        self.scroll_end(animate=False)

    def _anchor_messages(self) -> None:
        if self.max_scroll_y:
            self.anchor()

    def _scroll_messages_to_bottom_and_anchor(self) -> None:
        self._scroll_messages_to_bottom()
        self._anchor_messages()

    #

    async def append_stream_message_content(self, parts: ta.Sequence[StreamMessagePart]) -> None:
        # Live-tailing: if the view is pinned to the bottom when a streaming delta arrives, follow it down as the
        # message grows. The at-bottom check must happen *before* the append - growing the widget moves scroll_y off
        # the bottom, so checking after would always read as "not at bottom".
        scroll_to_bottom = False

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

                    if aim.is_mounted and self._is_messages_at_bottom():
                        scroll_to_bottom = True

                    await aim.append_stream_content(content)

            elif isinstance(part, FinalStreamMessagePart):
                if (msg := self._messages_by_uuid.get(part.message_uuid)) is None:
                    continue

                aim = check.isinstance(msg, part.message_cls)

                await aim.finalize_stream()

            else:
                raise TypeError(part)

        if scroll_to_bottom:
            self.call_after_refresh(self._scroll_messages_to_bottom_and_anchor)

    #

    async def mount_messages(self, *messages: Message) -> None:
        await self._mount_messages(*messages)

    async def mount_messages_before(self, anchor: Message, *messages: Message) -> None:
        """Mounts older messages above `anchor`, in order - the lazy-scrollback prepend path."""

        await self._mount_messages(*messages, before=anchor)

    async def _drain_mount_message_buffer(self) -> None:
        messages = await self._mount_message_buffer.swap()
        await self._mount_messages(*messages)

    async def _mount_messages(self, *messages: Message, before: Message | None = None) -> None:
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

            if before is not None:
                await self.mount(msg, before=before)
            else:
                await self.mount(msg)

            if mu is not None:
                self._messages_by_uuid[mu] = msg

            if isinstance(msg, StreamMessage):
                await msg.start_stream()

        if before is None and was_at_bottom:
            self.call_after_refresh(self._scroll_messages_to_bottom_and_anchor)

        if self._refresh_after_mount_messages:
            self._refresh_after_mount_messages = False
            self.refresh()
