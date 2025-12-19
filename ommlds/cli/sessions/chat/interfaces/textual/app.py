import asyncio
import typing as ta

from omdev.tui import textual as tx
from omlish import check
from omlish import lang
from omlish.logs import all as logs

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
from .widgets.messages import ToolConfirmationMessage
from .widgets.messages import UserMessage
from .widgets.messages import WelcomeMessage


log, alog = logs.get_module_loggers(globals())


##


ChatDriverEventQueue = ta.NewType('ChatDriverEventQueue', asyncio.Queue)


##


class ChatAppGetter(lang.CachedFunc0['ChatApp']):
    pass


class ChatApp(tx.App):
    ENABLE_COMMAND_PALETTE: ta.ClassVar[bool] = False

    def __init__(
            self,
            *,
            chat_driver: ChatDriver,
            chat_driver_event_queue: ChatDriverEventQueue,
    ) -> None:
        super().__init__()

        tx.setup_app_devtools(self, port=41932)

        self._chat_driver = chat_driver
        self._chat_driver_event_queue = chat_driver_event_queue

        self._chat_driver_action_queue: asyncio.Queue[ta.Any] = asyncio.Queue()

    def get_driver_class(self) -> type[tx.Driver]:
        return tx.get_pending_writes_driver_class(super().get_driver_class())

    CSS: ta.ClassVar[str] = read_app_css()

    #

    def compose(self) -> tx.ComposeResult:
        yield tx.VerticalScroll(id='messages-container')

        yield InputOuter(id='input-outer')

    #

    def _get_input_text_area(self) -> InputTextArea:
        return self.query_one('#input', InputTextArea)

    def _get_messages_container(self) -> tx.VerticalScroll:
        return self.query_one('#messages-container', tx.VerticalScroll)

    #

    def _is_messages_at_bottom(self, threshold: int = 3) -> bool:
        return (ms := self._get_messages_container()).scroll_y >= (ms.max_scroll_y - threshold)

    def _scroll_messages_to_bottom(self) -> None:
        self._get_messages_container().scroll_end(animate=False)

    def _anchor_messages(self) -> None:
        if (ms := self._get_messages_container()).max_scroll_y:
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

            self.call_after_refresh(self._scroll_messages_to_bottom)

            if was_at_bottom:
                self.call_after_refresh(self._anchor_messages)

        else:
            await self._mount_messages(StreamAiMessage(content))

    async def _mount_messages(self, *messages: tx.Widget) -> None:
        was_at_bottom = self._is_messages_at_bottom()

        msg_ctr = self._get_messages_container()

        for msg in [*(self._pending_mount_messages or []), *messages]:
            if isinstance(msg, (AiMessage, ToolConfirmationMessage)):
                await self._finalize_stream_ai_message()

            await msg_ctr.mount(msg)

            if isinstance(msg, StreamAiMessage):
                self._stream_ai_message = check.replacing_none(self._stream_ai_message, msg)
                await msg.write_initial_content()

        self._pending_mount_messages = None

        self.call_after_refresh(self._scroll_messages_to_bottom)

        if was_at_bottom:
            self.call_after_refresh(self._anchor_messages)

    #

    _chat_driver_event_task: asyncio.Task[None] | None = None

    @logs.async_exception_logging(alog)
    async def _chat_driver_event_task_main(self) -> None:
        while True:
            ev = await self._chat_driver_event_queue.get()
            if ev is None:
                break

            await alog.debug(lambda: f'Got chat driver event: {ev!r}')

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
                if isinstance(ev.delta, mc.ContentAiDelta):
                    cc = check.isinstance(ev.delta.c, str)
                    self.call_later(self._append_stream_ai_message_content, cc)

                elif isinstance(ev.delta, mc.ToolUseAiDelta):
                    pass

    #

    _chat_driver_action_task: asyncio.Task[None] | None = None

    @logs.async_exception_logging(alog)
    async def _chat_driver_action_task_main(self) -> None:
        while True:
            ac = await self._chat_driver_action_queue.get()
            if ac is None:
                break

            await alog.debug(lambda: f'Got chat driver action: {ac!r}')

            if isinstance(ac, mc.UserMessage):
                try:
                    await self._chat_driver.send_user_messages([ac])
                except Exception as e:  # noqa
                    raise

            else:
                raise TypeError(ac)  # noqa

    #

    async def on_mount(self) -> None:
        check.state(self._chat_driver_event_task is None)
        self._chat_driver_event_task = asyncio.create_task(self._chat_driver_event_task_main())

        await self._chat_driver.start()

        check.state(self._chat_driver_action_task is None)
        self._chat_driver_action_task = asyncio.create_task(self._chat_driver_action_task_main())

        self._get_input_text_area().focus()

        await self._mount_messages(
            WelcomeMessage(
                'Hello!',
            ),
        )

    async def on_unmount(self) -> None:
        if (cdt := self._chat_driver_event_task) is not None:
            await self._chat_driver_event_queue.put(None)
            await cdt

        await self._chat_driver.stop()

        if (cet := self._chat_driver_event_task) is not None:
            await self._chat_driver_event_queue.put(None)
            await cet

    @tx.on(InputTextArea.Submitted)
    async def on_input_text_area_submitted(self, event: InputTextArea.Submitted) -> None:
        self._get_input_text_area().clear()

        await self._finalize_stream_ai_message()

        await self._mount_messages(
            UserMessage(
                event.text,
            ),
        )

        await self._chat_driver_action_queue.put(mc.UserMessage(event.text))

    #

    async def confirm_tool_use(self, message: str) -> bool:
        fut: asyncio.Future[bool] = asyncio.get_running_loop().create_future()

        tcm = ToolConfirmationMessage(message, fut)

        async def inner() -> None:
            await self._mount_messages(tcm)

        self.call_later(inner)

        ret = await fut

        return ret
