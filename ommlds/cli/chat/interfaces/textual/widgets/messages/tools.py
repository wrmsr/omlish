# ruff: noqa: SLF001
import asyncio
import enum
import uuid

from omdev.tui import textual as tx
from omlish import check

from .base import Message
from .base import MessageFinalized
from .divider import MessageDivider


##


class ToolConfirmationControls(
    tx.InitAddClass,
    tx.Static,
):
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


class ToolMessage(Message):
    init_add_class = 'tool-message'

    class State(enum.StrEnum):
        RUNNING = 'running'
        COMPLETE = 'complete'
        DENIED = 'denied'
        CONFIRMING = 'confirming'

    def __init__(
            self,
            outer_content: tx.VisualType,
            inner_content: tx.VisualType,
            state: State,
            confirmation_fut: asyncio.Future[bool] | None = None,
            *,
            message_uuid: uuid.UUID | None = None,
    ) -> None:
        super().__init__(
            message_uuid=message_uuid,
        )

        self._outer_content = outer_content
        self._inner_content = inner_content
        self._state = state
        self._confirmation_fut = confirmation_fut

        self._has_rendered = False

    @property
    def message_content(self) -> None:
        return None

    @property
    def has_rendered(self) -> bool:
        return self._has_rendered

    @property
    def state(self) -> State:
        return self._state

    async def respond(self, allowed: bool) -> None:
        check.equal(self._state, ToolMessage.State.CONFIRMING)

        if allowed:
            self._state = ToolMessage.State.RUNNING
        else:
            self._state = ToolMessage.State.DENIED

        inner = self.query_one('.tool-message-inner')

        await inner.query_one(ToolConfirmationControls).remove()

        inner.remove_class('tool-message-inner-open')
        inner.add_class('tool-message-inner-closed')

        inner.query_one('.tool-message-outer-content', tx.Static).update(
            f'Tool use {"allowed" if allowed else "denied"}.',
        )

        if (cf := self._confirmation_fut) is not None:
            cf.set_result(allowed)
            self._confirmation_fut = None

        self.post_message(MessageFinalized(self))

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='tool-message-divider-container message-divider-container'):
            yield MessageDivider.for_message(self)

            with tx.Horizontal(classes='tool-message-outer message-outer'):
                yield tx.Static('? ', classes='tool-message-glyph message-glyph')
                with tx.Vertical(classes=' '.join([
                    'tool-message-inner',
                    'tool-message-inner-open',
                    'message-inner',
                ])):
                    yield tx.Static(self._outer_content, classes='tool-message-outer-content')
                    yield tx.Static(self._inner_content, classes='tool-message-inner-content')

                    yield ToolConfirmationControls(classes='tool-message-confirmation-controls')

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
