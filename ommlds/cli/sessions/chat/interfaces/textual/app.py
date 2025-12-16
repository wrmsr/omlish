import asyncio
import dataclasses as dc
import typing as ta

from omdev.tui import textual as tx
from omlish import check

from ...... import minichain as mc
from ...agents.agent import ChatAgent
from ...agents.events.types import AiMessagesChatEvent


##


ChatAgentEventQueue = ta.NewType('ChatAgentEventQueue', asyncio.Queue)


##


class WelcomeMessage(tx.Static):
    def __init__(self, content: str) -> None:
        super().__init__(content)

        self.add_class('welcome-message')


class UserMessage(tx.Static):
    def __init__(self, content: str) -> None:
        super().__init__(content)

        self.add_class('user-message')


class AiMessage(tx.Static):
    def __init__(self, content: str) -> None:
        super().__init__(content)

        self.add_class('ai-message')


##


class InputTextArea(tx.TextArea):
    @dc.dataclass()
    class Submitted(tx.Message):
        text: str

    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

    async def _on_key(self, event: tx.Key) -> None:
        if event.key == 'enter':
            event.prevent_default()
            event.stop()

            if text := self.text.strip():
                self.post_message(self.Submitted(text))

        else:
            await super()._on_key(event)


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

    CSS: ta.ClassVar[str] = """
        #messages-scroll {
            width: 100%;
            height: 1fr;

            padding: 0 2 0 2;
        }

        #messages-container {
            height: auto;
            width: 100%;

            margin-top: 1;
            margin-bottom: 0;

            layout: stream;
            text-align: left;
        }

        .welcome-message {
            margin: 1;

            border: round;

            padding: 1;

            text-align: center;
        }

        .user-message {
        }

        .ai-message {
        }

        #input-outer {
            width: 100%;
            height: auto;
        }

        #input-vertical {
            width: 100%;
            height: auto;

            margin: 0 2 1 2;

            padding: 0;
        }

        #input-vertical2 {
            width: 100%;
            height: auto;

            border: round $foreground-muted;

            padding: 0 1;
        }

        #input-horizontal {
            width: 100%;
            height: auto;
        }

        #input-glyph {
            width: auto;

            padding: 0 1 0 0;

            background: transparent;
            color: $primary;

            text-style: bold;
        }

        #input {
            width: 1fr;
            height: auto;
            max-height: 16;

            border: none;

            padding: 0;

            background: transparent;
            color: $text;
        }
    """

    ENABLE_COMMAND_PALETTE: ta.ClassVar[bool] = False

    #

    def compose(self) -> tx.ComposeResult:
        with tx.VerticalScroll(id='messages-scroll'):
            yield tx.Static(id='messages-container')

        with tx.Static(id='input-outer'):
            with tx.Vertical(id='input-vertical'):
                with tx.Vertical(id='input-vertical2'):
                    with tx.Horizontal(id='input-horizontal'):
                        yield tx.Static('>', id='input-glyph')
                        yield InputTextArea(placeholder='...', id='input')

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
