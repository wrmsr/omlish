import abc
import asyncio
import typing as ta

from omdev.tui import textual as tx
from omlish import check
from omlish import lang


##


class MessagesContainer(tx.VerticalScroll):
    pass


##


class MessageDivider(tx.Static):
    def __init__(self) -> None:
        super().__init__()

        self.add_class('message-divider')


##


class Message(tx.Static, lang.Abstract):
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*args, **kwargs)

        self.add_class('message')


#


class WelcomeMessage(Message):
    def __init__(self, content: str) -> None:
        super().__init__()

        self.add_class('welcome-message')

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='welcome-message-outer message-outer'):
            yield tx.Static(self._content, classes='welcome-message-content')


#


class UserMessage(Message):
    def __init__(self, content: str) -> None:
        super().__init__()

        self.add_class('user-message')

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='user-message-outer message-outer'):
            yield tx.Static('> ', classes='user-message-glyph message-glyph')
            with tx.Vertical(classes='user-message-inner message-inner'):
                yield tx.Static(self._content)


#


class AiMessage(Message, lang.Abstract):
    def __init__(self) -> None:
        super().__init__()

        self.add_class('ai-message')

    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='ai-message-outer message-outer'):
            yield tx.Static('< ', classes='ai-message-glyph message-glyph')
            with tx.Vertical(classes='ai-message-inner message-inner'):
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


class StreamAiMessage(AiMessage):
    def __init__(self, content: str) -> None:
        super().__init__()

        self._content = content

    def _compose_content(self) -> ta.Generator:
        yield tx.Markdown('')

    _stream_: tx.MarkdownStream | None = None

    def _stream(self) -> tx.MarkdownStream:
        if self._stream_ is None:
            self._stream_ = tx.Markdown.get_stream(self.query_one(tx.Markdown))
        return self._stream_

    async def write_initial_content(self) -> None:
        if self._content:
            await self._stream().write(self._content)

    async def append_content(self, content: str) -> None:
        if not content:
            return

        self._content += content
        await self._stream().write(content)

    async def stop_stream(self) -> None:
        if (stream := self._stream_) is None:
            return

        await stream.stop()
        self._stream_ = None


#


class ToolConfirmationControls(tx.Static):
    class ClickedAllow(tx.Message):
        pass

    class ClickedDeny(tx.Message):
        pass

    def compose(self) -> tx.ComposeResult:
        yield tx.Button('Allow', action='allow')
        yield tx.Button('Deny', action='deny')

    def action_allow(self) -> None:
        self.post_message(self.ClickedAllow())

    def action_deny(self) -> None:
        self.post_message(self.ClickedDeny())


class ToolConfirmationMessage(Message):
    def __init__(
            self,
            outer_content: str,
            inner_content: str,
            fut: asyncio.Future[bool],
    ) -> None:
        super().__init__()

        self.add_class('tool-confirmation-message')

        self._outer_content = outer_content
        self._inner_content = inner_content
        self._fut = fut

        self._has_rendered = False
        self._has_responded = False

    @property
    def has_rendered(self) -> bool:
        return self._has_rendered

    @property
    def has_responded(self) -> bool:
        return self._has_responded

    async def respond(self, allowed: bool) -> None:
        check.equal(self._fut.done(), self._has_responded)

        if self._has_responded:
            return
        self._has_responded = True

        inner = self.query_one(tx.Vertical)

        await inner.query_one(ToolConfirmationControls).remove()

        inner.remove_class('tool-confirmation-message-inner-open')
        inner.add_class('tool-confirmation-message-inner-closed')

        inner.query_one('.tool-confirmation-message-outer-content', tx.Static).update(
            f'Tool use {"allowed" if allowed else "denied"}.',
        )

        self._fut.set_result(allowed)

    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='tool-confirmation-message-outer message-outer'):
            yield tx.Static('? ', classes='tool-confirmation-message-glyph message-glyph')
            with tx.Vertical(classes=' '.join([
                'tool-confirmation-message-inner',
                'tool-confirmation-message-inner-open',
                'message-inner',
            ])):
                yield tx.Static(self._outer_content, classes='tool-confirmation-message-outer-content')
                yield tx.Static(self._inner_content, classes='tool-confirmation-message-inner-content')

                yield ToolConfirmationControls(classes='tool-confirmation-message-controls')

    def on_mount(self) -> None:
        def inner():
            self._has_rendered = True

        self.call_after_refresh(inner)

    @tx.on(ToolConfirmationControls.ClickedAllow)
    async def on_clicked_allow(self, event: ToolConfirmationControls.ClickedAllow) -> None:
        await self.respond(True)

    @tx.on(ToolConfirmationControls.ClickedDeny)
    async def on_clicked_deny(self, event: ToolConfirmationControls.ClickedDeny) -> None:
        await self.respond(False)


#


class UiMessage(Message):
    def __init__(self, content: str) -> None:
        super().__init__()

        self.add_class('ui-message')

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='ui-message-outer message-outer'):
            yield tx.Static('~ ', classes='ui-message-glyph message-glyph')
            with tx.Vertical(classes='ui-message-inner message-inner'):
                yield tx.Static(self._content)
