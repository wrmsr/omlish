import typing as ta

from omdev.tui import textual as tx


##


class ChatApp(tx.App):
    def __init__(
            self,
    ) -> None:
        super().__init__()

    CSS: ta.ClassVar[str] = """
    #messages-scroll {
    }

    #messages {
    }

    #input-outer {
    }

    #input-vertical {
    }

    #input-horizontal {
    }

    #input-glyph {
    }

    #input {
    }
    """

    ENABLE_COMMAND_PALETTE: ta.ClassVar[bool] = False

    def compose(self) -> tx.ComposeResult:
        with tx.VerticalScroll(id='messages-scroll'):
            yield tx.Static(id='messages')

        with tx.Static(id='input-outer'):
            with tx.Vertical(id='input-vertical'):
                with tx.Horizontal(id='input-horizontal'):
                    yield tx.Static('>', id='input-glyph')
                    yield tx.TextArea(placeholder='...', id='input')

    async def on_mount(self) -> None:
        await self.query_one('#messages').mount(tx.Static('Hi!'))
