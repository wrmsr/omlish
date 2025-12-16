import dataclasses as dc
import typing as ta

from omdev.tui import textual as tx


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


class InputOuter(tx.Static):
    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(id='input-vertical'):
            with tx.Vertical(id='input-vertical2'):
                with tx.Horizontal(id='input-horizontal'):
                    yield tx.Static('>', id='input-glyph')
                    yield InputTextArea(placeholder='...', id='input')
