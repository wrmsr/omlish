import asyncio
import dataclasses as dc
import io
import typing as ta

from omdev.tui import textual as tx
from omlish import check
from omlish import lang

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
        super().__init__()

        self.add_class('user-message')

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='user-message-outer'):
            yield tx.Static('> ', classes='user-message-glyph')
            with tx.Vertical(classes='user-message-inner'):
                yield tx.Static(self._content)


class AiMessage(tx.Static):
    def __init__(self, content: str) -> None:
        super().__init__()

        self.add_class('ai-message')

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='ai-message-outer'):
            yield tx.Static('< ', classes='ai-message-glyph')
            with tx.Vertical(classes='ai-message-inner'):
                yield tx.Static(self._content)


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


@lang.cached_function
def _read_app_css() -> str:
    tcss_rsrcs = [
        rsrc
        for rsrc in lang.get_relative_resources('.styles', globals=globals()).values()
        if rsrc.name.endswith('.tcss')
    ]

    out = io.StringIO()

    for i, rsrc in enumerate(tcss_rsrcs):
        if i:
            out.write('\n\n')

        out.write(f'/*** {rsrc.name} ***/\n')
        out.write('\n')

        out.write(rsrc.read_text().strip())
        out.write('\n')

    return out.getvalue()


#


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

    CSS: ta.ClassVar[str] = _read_app_css()

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
