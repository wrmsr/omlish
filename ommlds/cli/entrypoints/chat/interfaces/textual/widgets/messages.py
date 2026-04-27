import abc
import asyncio
import io
import typing as ta
import uuid

from omdev.tui import textual as tx
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.logs import all as logs


log, alog = logs.get_module_loggers(globals())


##


class MessageDivider(tx.InitAddClass, tx.Static):
    init_add_class = 'message-divider'

    def __init__(
            self,
            text: str | None = None,
            *,
            align: tx.AlignMethod = 'center',
            line_style: ta.Any | None = None,
            text_style: ta.Any | None = None,
    ) -> None:
        super().__init__()

        if text is None:
            text = lang.localnow().strftime('%Y-%m-%d %H:%M:%S')

        self._text = text
        self._align = align
        self._line_style = line_style
        self._text_style = text_style

        self._refresh()

    def set_text(self, text: str) -> None:
        self._text = text
        self._refresh()

    def set_align(self, align: tx.AlignMethod) -> None:
        self._align = align
        self._refresh()

    def _refresh(self) -> None:
        if (text_style := self._text_style) is None:
            text_style = tx.RichStyle(color=self.rich_style.color)

        text = tx.Text(
            self._text,
            style=text_style,
        ) if self._text else ''

        if (line_style := self._line_style) is None:
            line_style = tx.RichStyle(color=self.app.current_theme.primary)

        self.update(
            tx.RichRule(
                text,
                align=self._align,
                style=line_style,
            ),
        )


##


@dc.dataclass()
class MessageFinalized(tx.Event):
    widget: tx.Widget


class OnMountMessageFinalized(tx.Widget, lang.Abstract):
    __has_finalized = False

    @tx.on(tx.Mount)
    async def _on_mount_message_finalize(self, event: tx.Mount) -> None:
        if not self.__has_finalized:
            self.__has_finalized = True

            self.post_message(MessageFinalized(self))


##


class Message(tx.InitAddClass, tx.Static, lang.Abstract):
    init_add_class = 'message'

    def __init__(
            self,
            *,
            message_uuid: uuid.UUID | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._message_uuid = message_uuid

    @property
    def message_uuid(self) -> uuid.UUID | None:
        return self._message_uuid


class StaticMessage(OnMountMessageFinalized, Message, lang.Abstract):
    pass


##


class WelcomeMessage(StaticMessage):
    init_add_class = 'welcome-message'

    def __init__(
            self,
            content: tx.VisualType,
            *,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='welcome-message-outer message-outer'):
            yield tx.Static(self._content, classes='welcome-message-content')


##


class UserMessage(StaticMessage):
    init_add_class = 'user-message'

    def __init__(
            self,
            content: tx.VisualType,
            *,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='user-message-divider-container message-divider-container'):
            yield MessageDivider()

            with tx.Horizontal(classes='user-message-outer message-outer'):
                yield tx.Static('> ', classes='user-message-glyph message-glyph')
                with tx.Vertical(classes='user-message-inner message-inner'):
                    yield tx.Static(self._content)


##


class AiMessage(Message, lang.Abstract):
    init_add_class = 'ai-message'

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='ai-message-divider-container message-divider-container'):
            yield MessageDivider()

            with tx.Horizontal(classes='ai-message-outer message-outer'):
                yield tx.Static('< ', classes='ai-message-glyph message-glyph')
                with tx.Vertical(classes='ai-message-inner message-inner'):
                    yield from self._compose_content()

    @abc.abstractmethod
    def _compose_content(self) -> ta.Generator:
        raise NotImplementedError


##


class StaticAiMessage(StaticMessage, AiMessage):
    init_add_class = 'static-ai-message'

    def __init__(
            self,
            content: str,
            *,
            markdown: bool = False,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

        self._content = content
        self._markdown = markdown

    def _compose_content(self) -> ta.Generator:
        if self._markdown:
            yield tx.Markdown(self._content)
        else:
            yield tx.Static(self._content)


##


StreamAiMessageState: ta.TypeAlias = ta.Literal[  # noqa
    'new',
    'new_finalizing',
    'streaming',
    'finalized',
]


@dc.dataclass(frozen=True)
class StreamAiMessagePart(lang.Abstract):
    message_uuid: uuid.UUID


@dc.dataclass(frozen=True)
class ContentStreamAiMessagePart(StreamAiMessagePart):
    content: str


@dc.dataclass(frozen=True)
class FinalStreamAiMessagePart(StreamAiMessagePart):
    pass


class StreamAiMessage(AiMessage):
    init_add_class = 'stream-ai-message'

    def __init__(
            self,
            *initial_contents: str,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

        self._initial_contents: list[str] = list(initial_contents)

        self._state: StreamAiMessageState = 'new'

    @property
    def state(self) -> StreamAiMessageState:
        return self._state

    def _compose_content(self) -> ta.Generator:
        yield tx.Markdown('')

    #

    _final_content: str

    @property
    def final_content(self) -> str:
        check.state(self._state == 'finalized')
        return self._final_content

    #

    _stream_content: io.StringIO
    _stream: tx.MarkdownStream

    async def start_stream(self) -> None:
        check.state(self._state in ('new', 'new_finalizing'))

        self._stream_content = io.StringIO()
        self._stream = tx.Markdown.get_stream(self.query_one(tx.Markdown))

        if (ics := self._initial_contents):
            for ic in ics:
                self._stream_content.write(ic)
                await self._stream.write(ic)

        del self._initial_contents

        if self._state == 'new':
            self._state = 'streaming'

        elif self._state == 'new_finalizing':
            await self._finalize_stream()

        else:
            raise RuntimeError(f'unexpected state: {self._state}')

    async def append_stream_content(self, content: str) -> None:
        if not content:
            return

        if self._state == 'new':
            self._initial_contents.append(content)

        elif self._state == 'streaming':
            self._stream_content.write(content)
            await self._stream.write(content)

        else:
            raise RuntimeError(f'unexpected state: {self._state}')

    async def _finalize_stream(self) -> None:
        await self._stream.stop()
        del self._stream

        self._final_content = self._stream_content.getvalue()
        del self._stream_content

        self._state = 'finalized'

        self.post_message(MessageFinalized(self))

    async def finalize_stream(self) -> None:
        if self._state == 'new':
            self._state = 'new_finalizing'

        elif self._state == 'streaming':
            await self._finalize_stream()

        else:
            raise RuntimeError(f'unexpected state: {self._state}')


##


class ToolConfirmationControls(tx.InitAddClass, tx.Static):
    init_add_class = 'tool-confirmation-controls'

    class ClickedAllow(tx.Message):
        pass

    class ClickedDeny(tx.Message):
        pass

    def compose(self) -> tx.ComposeResult:
        yield tx.Button('Allow (F10)', action='allow')
        yield tx.Button('Deny (F2)', action='deny')

    def action_allow(self) -> None:
        self.post_message(self.ClickedAllow())

    def action_deny(self) -> None:
        self.post_message(self.ClickedDeny())


class ToolConfirmationMessage(Message):
    init_add_class = 'tool-confirmation-message'

    def __init__(
            self,
            outer_content: tx.VisualType,
            inner_content: tx.VisualType,
            fut: asyncio.Future[bool],
            *,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

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

        inner = self.query_one('.tool-confirmation-message-inner')

        await inner.query_one(ToolConfirmationControls).remove()

        inner.remove_class('tool-confirmation-message-inner-open')
        inner.add_class('tool-confirmation-message-inner-closed')

        inner.query_one('.tool-confirmation-message-outer-content', tx.Static).update(
            f'Tool use {"allowed" if allowed else "denied"}.',
        )

        self._fut.set_result(allowed)

        self.post_message(MessageFinalized(self))

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='tool-confirmation-message-divider-container message-divider-container'):
            yield MessageDivider()

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


##


class UiMessage(StaticMessage):
    init_add_class = 'ui-message'

    def __init__(
            self,
            content: tx.VisualType,
            *,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

        self._content = content

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='ui-message-divider-container message-divider-container'):
            yield MessageDivider()

            with tx.Horizontal(classes='ui-message-outer message-outer'):
                yield tx.Static('~ ', classes='ui-message-glyph message-glyph')
                with tx.Vertical(classes='ui-message-inner message-inner'):
                    yield tx.Static(self._content)


##


class MessagesContainer(tx.InitAddClass, tx.ComposeOnce, tx.VerticalScroll):
    init_add_class = 'messages-container'

    def __init__(self, init_messages: ta.Sequence[Message] | None = None) -> None:
        super().__init__()

        self._messages_by_uuid: dict[uuid.UUID, Message] = {}

        if init_messages:
            self._pending_mount_messages = list(init_messages)

    #

    def _compose_once(self) -> tx.ComposeResult:
        return
        yield  # noqa

    #

    def _is_messages_at_bottom(self, threshold: int = 3) -> bool:
        return self.scroll_y >= (self.max_scroll_y - threshold)

    def _scroll_messages_to_bottom(self) -> None:
        self.scroll_end(animate=False)

    def _anchor_messages(self) -> None:
        if self.max_scroll_y:
            self.anchor()

    def _scroll_messages_to_bottom_and_anchor(self) -> None:
        self._scroll_messages_to_bottom()
        self._anchor_messages()

    #

    _pending_mount_messages: list[Message] | None = None

    async def enqueue_mount_messages(self, *messages: Message) -> None:
        if (lst := self._pending_mount_messages) is None:
            lst = self._pending_mount_messages = []

        lst.extend(messages)

    #

    async def append_stream_ai_message_content(self, parts: ta.Sequence[StreamAiMessagePart]) -> None:
        mount_messages = False
        refresh = False
        scroll_to_bottom = False

        for part in parts:
            if isinstance(part, ContentStreamAiMessagePart):
                message_uuid = part.message_uuid
                content = part.content

                if (msg := self._messages_by_uuid.get(message_uuid)) is None:
                    aim = StreamAiMessage(content, message_uuid=message_uuid)

                    self._messages_by_uuid[message_uuid] = aim

                    await self.enqueue_mount_messages(aim)

                    mount_messages = True
                    refresh = True

                else:
                    aim = check.isinstance(msg, StreamAiMessage)

                    if aim.is_mounted:
                        scroll_to_bottom |= self._is_messages_at_bottom()

                    await aim.append_stream_content(content)

            elif isinstance(part, FinalStreamAiMessagePart):
                if (msg := self._messages_by_uuid.get(part.message_uuid)) is None:
                    continue

                aim = check.isinstance(msg, StreamAiMessage)

                await aim.finalize_stream()

            else:
                raise TypeError(part)

        if mount_messages:
            self.call_later(self.mount_messages)
        if scroll_to_bottom:
            self.call_after_refresh(self._scroll_messages_to_bottom_and_anchor)
        if refresh:
            self.refresh()

    #

    async def mount_messages(self, *messages: Message) -> None:
        was_at_bottom = self._is_messages_at_bottom()

        for msg in [*(self._pending_mount_messages or []), *messages]:
            if (mu := msg.message_uuid) is not None:
                try:
                    xm = self._messages_by_uuid[mu]
                except KeyError:
                    pass
                else:
                    if not (isinstance(msg, StreamAiMessage) and xm is msg):
                        raise ValueError(f'message uuid already in use: {mu}')

            await self.mount(msg)

            if mu is not None:
                self._messages_by_uuid[mu] = msg

            if isinstance(msg, StreamAiMessage):
                await msg.start_stream()

        self._pending_mount_messages = None

        self.call_after_refresh(self._scroll_messages_to_bottom)

        if was_at_bottom:
            self.call_after_refresh(self._anchor_messages)
