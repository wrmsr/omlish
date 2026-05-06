# ruff: noqa: SLF001
import asyncio
import enum
import typing as ta

from omdev.tui import textual as tx
from omlish import check

from .base import Message
from .base import MessageFinalized
from .divider import MessageDivider


##


class ToolMessage(Message):
    init_add_class = 'tool-message'

    class State(enum.StrEnum):
        RUNNING = 'running'
        COMPLETE = 'complete'
        CONFIRMING = 'confirming'
        DENIED = 'denied'
        FAILED = 'failed'

    def __init__(
            self,
            outer_content: tx.VisualType,
            inner_content: tx.VisualType | None,
            state: State,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._outer_content = outer_content
        self._inner_content = inner_content
        self._state = state

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

    def compose(self) -> tx.ComposeResult:
        with tx.Vertical(classes='tool-message-divider-container message-divider-container'):
            yield MessageDivider.for_message(self)

            with tx.Horizontal(classes='tool-message-outer message-outer'):
                yield tx.Static('* ', classes='tool-message-glyph message-glyph')
                with tx.Vertical(classes='tool-message-inner message-inner'):
                    with tx.Horizontal(classes='tool-message-summary-row'):
                        if self._inner_content is not None:
                            yield tx.Static(tx.Text('[+]'), classes='tool-message-expand-button')

                        yield tx.Static(self._outer_content, classes='tool-message-outer-content')

                    if self._inner_content is not None:
                        yield tx.Static(self._inner_content, classes='tool-message-inner-content')

    def on_mount(self) -> None:
        def inner():
            self._has_rendered = True

        self.call_after_refresh(inner)

    def toggle_inner_content(self) -> None:
        xb = check.isinstance(self.query_one('.tool-message-expand-button'), tx.Static)
        ic = check.isinstance(self.query_one('.tool-message-inner-content'), tx.Static)
        if ic.styles.display == 'none':
            xb.content = tx.Text('[-]')
            ic.styles.display = 'block'
        else:
            xb.content = tx.Text('[+]')
            ic.styles.display = 'none'

    def on_click(self, event: tx.Click) -> None:
        if (wx := event.widget) is not None:
            if 'tool-message-expand-button' in wx.classes:
                event.stop()
                self.toggle_inner_content()
                return


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


class ToolConfirmationMessage(Message):
    init_add_class = 'tool-confirmation-message'

    def __init__(
            self,
            outer_content: tx.VisualType,
            inner_content: tx.VisualType,
            fut: asyncio.Future[bool],
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._outer_content = outer_content
        self._inner_content = inner_content
        self._fut = fut

        self._has_rendered = False
        self._has_responded = False

    @property
    def message_content(self) -> None:
        return None

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
            yield MessageDivider.for_message(self)

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
