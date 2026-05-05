# ruff: noqa: SLF001
import typing as ta
import uuid

from omdev import clipboard as cpb
from omdev.tui import textual as tx
from omlish import check

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
            init_messages: ta.Sequence[Message] | None = None,
            *,
            clipboard: cpb.Clipboard | None = None,
    ) -> None:
        super().__init__()

        self._clipboard = clipboard

        self._messages_by_uuid: dict[uuid.UUID, Message] = {}

        if init_messages:
            self._pending_mount_messages = list(init_messages)

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

    _pending_mount_messages: list[Message] | None = None

    async def enqueue_mount_messages(self, *messages: Message) -> None:
        if (lst := self._pending_mount_messages) is None:
            lst = self._pending_mount_messages = []

        lst.extend(messages)

    #

    async def append_stream_message_content(self, parts: ta.Sequence[StreamMessagePart]) -> None:
        mount_messages = False
        refresh = False
        scroll_to_bottom = False

        for part in parts:
            if isinstance(part, ContentStreamMessagePart):
                message_uuid = part.message_uuid
                content = part.content

                if (msg := self._messages_by_uuid.get(message_uuid)) is None:
                    aim = part.message_cls(content, message_uuid=message_uuid)

                    self._messages_by_uuid[message_uuid] = aim

                    await self.enqueue_mount_messages(aim)

                    mount_messages = True
                    refresh = True

                else:
                    aim = check.isinstance(msg, part.message_cls)

                    if aim.is_mounted:
                        scroll_to_bottom |= self._is_messages_at_bottom()

                    await aim.append_stream_content(content)

            elif isinstance(part, FinalStreamMessagePart):
                if (msg := self._messages_by_uuid.get(part.message_uuid)) is None:
                    continue

                aim = check.isinstance(msg, part.message_cls)

                await aim.finalize_stream()

            else:
                raise TypeError(part)

        if mount_messages:
            self.call_later(self.mount_messages)
        if scroll_to_bottom:
            self.call_after_refresh(self._scroll_messages_to_bottom_and_anchor)
        if refresh:
            self.refresh()

    #

    async def mount_messages(self, *messages: Message) -> None:
        was_at_bottom = self._is_messages_at_bottom()

        for msg in [*(self._pending_mount_messages or []), *messages]:
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

        self._pending_mount_messages = None

        self.call_after_refresh(self._scroll_messages_to_bottom)

        if was_at_bottom:
            self.call_after_refresh(self._anchor_messages)
