import dataclasses as dc
import typing as ta

from omdev.tui import textual as tx


##


class UserMessage(tx.Static):
    pass


class AiMessage(tx.Static):
    pass


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
    ) -> None:
        super().__init__()

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

    async def _mount_message(self, *messages: tx.Widget) -> None:
        msg_ctr = self._get_messages_container()

        for msg in messages:
            await msg_ctr.mount(msg)

        self.call_after_refresh(lambda: msg_ctr.scroll_end(animate=False))

    #

    async def on_mount(self) -> None:
        self._get_input_text_area().focus()

        await self._mount_message(UserMessage('Hello!'))

    async def on_input_text_area_submitted(self, event: InputTextArea.Submitted) -> None:
        self._get_input_text_area().clear()

        await self._mount_message(
            UserMessage(event.text),
            AiMessage(f'You said: {event.text}!'),
        )
