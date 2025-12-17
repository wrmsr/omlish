import abc
import typing as ta

from omdev.tui import textual as tx
from omlish import lang


##


class Message(tx.Static, lang.Abstract):
    pass


##


class WelcomeMessage(Message):
    def __init__(self, content: str) -> None:
        super().__init__(content)

        self.add_class('welcome-message')


##


class UserMessage(Message):
    def __init__(self, content: str) -> None:
        super().__init__()

        self.add_class('user-message')

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='user-message-outer'):
            yield tx.Static('> ', classes='user-message-glyph')
            with tx.Vertical(classes='user-message-inner'):
                yield tx.Static(self._content)


##


class AiMessage(Message, lang.Abstract):
    def __init__(self) -> None:
        super().__init__()

        self.add_class('ai-message')

    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='ai-message-outer'):
            yield tx.Static('< ', classes='ai-message-glyph')
            with tx.Vertical(classes='ai-message-inner'):
                yield from self._compose_content()

    @abc.abstractmethod
    def _compose_content(self) -> ta.Generator:
        raise NotImplementedError


class StaticAiMessage(AiMessage):
    def __init__(
            self,
            content: str,
            *,
            markdown: bool = False,
    ) -> None:
        super().__init__()

        self._content = content
        self._markdown = markdown

    def _compose_content(self) -> ta.Generator:
        if self._markdown:
            yield tx.Markdown(self._content)
        else:
            yield tx.Static(self._content)
