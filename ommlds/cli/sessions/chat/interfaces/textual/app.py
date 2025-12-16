import asyncio
import typing as ta

from omdev.tui import textual as tx
from omlish import check

from ...... import minichain as mc
from ...agents.agent import ChatAgent
from ...agents.events.types import AiMessagesChatEvent
from .styles import read_app_css
from .widgets.input import InputOuter
from .widgets.input import InputTextArea
from .widgets.messages import AiMessage
from .widgets.messages import UserMessage
from .widgets.messages import WelcomeMessage


##


ChatAgentEventQueue = ta.NewType('ChatAgentEventQueue', asyncio.Queue)


##


class ChatApp(tx.App):
    def __init__(
            self,
            *,
            agent: ChatAgent,
            event_queue: ChatAgentEventQueue,
    ) -> None:
        super().__init__()

        self._agent = agent
        self._event_queue = event_queue

    CSS: ta.ClassVar[str] = read_app_css()

    ENABLE_COMMAND_PALETTE: ta.ClassVar[bool] = False

    #

    def compose(self) -> tx.ComposeResult:
        with tx.VerticalScroll(id='messages-scroll'):
            yield tx.Static(id='messages-container')

        yield InputOuter(id='input-outer')

    #

    def _get_input_text_area(self) -> InputTextArea:
        return self.query_one('#input', InputTextArea)

    def _get_messages_container(self) -> tx.Static:
        return self.query_one('#messages-container', tx.Static)

    #

    _pending_mount_messages: list[tx.Widget] | None = None

    async def _enqueue_mount_messages(self, *messages: tx.Widget) -> None:
        if (lst := self._pending_mount_messages) is None:
            lst = self._pending_mount_messages = []

        lst.extend(messages)

    async def _mount_messages(self, *messages: tx.Widget) -> None:
        msg_ctr = self._get_messages_container()

        for msg in [*(self._pending_mount_messages or []), *messages]:
            await msg_ctr.mount(msg)

        self._pending_mount_messages = None

        self.call_after_refresh(lambda: msg_ctr.scroll_end(animate=False))

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
                            AiMessage(
                                check.isinstance(ai_msg.c, str),
                            ),
                        )

                if wx:
                    await self._enqueue_mount_messages(*wx)
                    self.call_later(self._mount_messages)

    #

    async def on_mount(self) -> None:
        check.state(self._event_queue_task is None)
        self._event_queue_task = asyncio.create_task(self._event_queue_task_main())

        await self._agent.start()

        self._get_input_text_area().focus()

        await self._mount_messages(
            WelcomeMessage(
                'Hello!',
            ),
        )

    async def on_unmount(self) -> None:
        await self._agent.stop()

        if (eqt := self._event_queue_task) is not None:
            await self._event_queue.put(None)
            await eqt

    async def on_input_text_area_submitted(self, event: InputTextArea.Submitted) -> None:
        self._get_input_text_area().clear()

        await self._mount_messages(
            UserMessage(
                event.text,
            ),
        )

        await self._agent.send_user_messages([mc.UserMessage(event.text)])
