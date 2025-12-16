from omdev.tui import textual as tx


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
