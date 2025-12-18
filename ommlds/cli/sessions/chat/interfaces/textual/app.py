import asyncio
import typing as ta

from omdev.tui import textual as tx
from omlish import check

from ...... import minichain as mc
from ...drivers.driver import ChatDriver
from ...drivers.events.types import AiDeltaChatEvent
from ...drivers.events.types import AiMessagesChatEvent
from .styles import read_app_css
from .widgets.input import InputOuter
from .widgets.input import InputTextArea
from .widgets.messages import AiMessage
from .widgets.messages import StaticAiMessage
from .widgets.messages import StreamAiMessage
from .widgets.messages import UserMessage
from .widgets.messages import WelcomeMessage


##


ChatDriverEventQueue = ta.NewType('ChatDriverEventQueue', asyncio.Queue)


##


class ChatApp(tx.App):
    ENABLE_COMMAND_PALETTE: ta.ClassVar[bool] = False

    def __init__(
            self,
            *,
            driver: ChatDriver,
            event_queue: ChatDriverEventQueue,
    ) -> None:
        super().__init__()

        self._chat_driver = driver
        self._event_queue = event_queue

    def get_driver_class(self) -> type[tx.Driver]:
        return tx.get_pending_writes_driver_class(super().get_driver_class())

    CSS: ta.ClassVar[str] = read_app_css()

    #

    def compose(self) -> tx.ComposeResult:
        with tx.VerticalScroll(id='messages-scroll'):
            yield tx.Static(id='messages-container')

        yield InputOuter(id='input-outer')

    #

    def _get_input_text_area(self) -> InputTextArea:
        return self.query_one('#input', InputTextArea)

    def _get_messages_scroll(self) -> tx.VerticalScroll:
        return self.query_one('#messages-scroll', tx.VerticalScroll)

    def _get_messages_container(self) -> tx.Static:
        return self.query_one('#messages-container', tx.Static)

    #

    def _is_messages_at_bottom(self, threshold: int = 3) -> bool:
        return (ms := self._get_messages_scroll()).scroll_y >= (ms.max_scroll_y - threshold)

    def _scroll_messages_to_bottom(self) -> None:
        self._get_messages_scroll().scroll_end(animate=False)

    def _anchor_messages(self) -> None:
        if (ms := self._get_messages_scroll()).max_scroll_y:
            ms.anchor()

    #

    _pending_mount_messages: list[tx.Widget] | None = None

    async def _enqueue_mount_messages(self, *messages: tx.Widget) -> None:
        if (lst := self._pending_mount_messages) is None:
            lst = self._pending_mount_messages = []

        lst.extend(messages)

    _stream_ai_message: StreamAiMessage | None = None

    async def _finalize_stream_ai_message(self) -> None:
        if self._stream_ai_message is None:
            return

        await self._stream_ai_message.stop_stream()
        self._stream_ai_message = None

    async def _append_stream_ai_message_content(self, content: str) -> None:
        if (sam := self._stream_ai_message) is not None:
            was_at_bottom = self._is_messages_at_bottom()

            await sam.append_content(content)

            self.call_after_refresh(lambda: self._get_messages_container().scroll_end(animate=False))

            if was_at_bottom:
                self.call_after_refresh(self._anchor_messages)

        else:
            await self._mount_messages(StreamAiMessage(content))

    async def _mount_messages(self, *messages: tx.Widget) -> None:
        was_at_bottom = self._is_messages_at_bottom()

        msg_ctr = self._get_messages_container()

        for msg in [*(self._pending_mount_messages or []), *messages]:
            if isinstance(msg, AiMessage):
                await self._finalize_stream_ai_message()

            await msg_ctr.mount(msg)

            if isinstance(msg, StreamAiMessage):
                self._stream_ai_message = check.replacing_none(self._stream_ai_message, msg)
                await msg.write_initial_content()

        self._pending_mount_messages = None

        self.call_after_refresh(lambda: msg_ctr.scroll_end(animate=False))

        if was_at_bottom:
            self.call_after_refresh(self._anchor_messages)

    #

    _event_queue_task: asyncio.Task[None] | None = None

    async def _event_queue_task_main(self) -> None:
        while True:
            ev = await self._event_queue.get()
            if ev is None:
                break

            if isinstance(ev, AiMessagesChatEvent):
                wx: list[tx.Widget] = []

                for ai_msg in ev.chat:
                    if isinstance(ai_msg, mc.AiMessage):
                        wx.append(
                            StaticAiMessage(
                                check.isinstance(ai_msg.c, str),
                                markdown=True,
                            ),
                        )

                if wx:
                    await self._enqueue_mount_messages(*wx)
                    self.call_later(self._mount_messages)

            elif isinstance(ev, AiDeltaChatEvent):
                cd = check.isinstance(ev.delta, mc.ContentAiDelta)
                cc = check.isinstance(cd.c, str)
                self.call_later(self. _append_stream_ai_message_content, cc)

    #

    # def _schedule_after_refresh(self) -> None:
    #     self.call_after_refresh(self._after_refresh)

    # def _after_refresh(self) -> None:
    #     self.after_repaint()
    #
    #     self._schedule_after_refresh()

    # def after_repaint(self) -> None:
    #     # from omdev.tui.textual.debug.dominfo import inspect_dom_node  # noqa
    #
    #     pass

    #

    async def on_mount(self) -> None:
        # self._schedule_after_refresh()

        check.state(self._event_queue_task is None)
        self._event_queue_task = asyncio.create_task(self._event_queue_task_main())

        await self._chat_driver.start()

        self._get_input_text_area().focus()

        await self._mount_messages(
            WelcomeMessage(
                'Hello!',
            ),
        )

    async def on_unmount(self) -> None:
        await self._chat_driver.stop()

        if (eqt := self._event_queue_task) is not None:
            await self._event_queue.put(None)
            await eqt

    async def on_input_text_area_submitted(self, event: InputTextArea.Submitted) -> None:
        self._get_input_text_area().clear()

        await self._finalize_stream_ai_message()

        await self._mount_messages(
            UserMessage(
                event.text,
            ),
        )

        await self._chat_driver.send_user_messages([mc.UserMessage(event.text)])
