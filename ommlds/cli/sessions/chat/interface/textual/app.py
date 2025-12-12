import typing as ta

from omdev.tui import textual as tx


##


class InputTextArea(tx.TextArea):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)


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

        #messages {
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

    def compose(self) -> tx.ComposeResult:
        with tx.VerticalScroll(id='messages-scroll'):
            yield tx.Static(id='messages')

        with tx.Static(id='input-outer'):
            with tx.Vertical(id='input-vertical'):
                with tx.Vertical(id='input-vertical2'):
                    with tx.Horizontal(id='input-horizontal'):
                        yield tx.Static('>', id='input-glyph')
                        yield InputTextArea(placeholder='...', id='input')

    async def on_mount(self) -> None:
        await self.query_one('#messages').mount(tx.Static('Hi!'))
