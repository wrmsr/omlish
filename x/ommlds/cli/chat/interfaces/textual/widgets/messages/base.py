# ruff: noqa: SLF001
import abc
import typing as ta
import uuid

from omdev import clipboard as cpb
from omdev.tui import textual as tx
from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .divider import MessageDividerClicked


with lang.auto_proxy_import(globals()):
    from . import container


##


@dc.dataclass()
class MessageFinalized(tx.Event):
    widget: tx.Widget


class OnMountMessageFinalized(
    tx.Widget,
    lang.Abstract,
):
    __has_finalized = False

    @tx.on(tx.Mount)
    async def _on_mount_message_finalize(self, event: tx.Mount) -> None:
        if not self.__has_finalized:
            self.__has_finalized = True

            self.post_message(MessageFinalized(self))


##


class Message(
    tx.InitAddClass,
    tx.Static,
    lang.Abstract,
):
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
    def messages_container(self) -> container.MessagesContainer:
        return check.not_none(tx.find_ancestor(container.MessagesContainer, self))

    @property
    @abc.abstractmethod
    def message_content(self) -> ta.Any | None:
        raise NotImplementedError

    @property
    def message_uuid(self) -> uuid.UUID | None:
        return self._message_uuid

    @tx.on(MessageDividerClicked)
    async def _on_message_divider_clicked(self, event: MessageDividerClicked) -> None:
        event.stop()

        actions: list[tuple[str, ta.Callable]] = []

        if (clipboard := self.messages_container._clipboard) is not None:
            if (mu := self._message_uuid) is not None:
                def copy_mu() -> None:
                    clipboard.put(cpb.TextClipboardContents(str(mu)))

                actions.append(('Copy Id', copy_mu))

            if (content := self.message_content) is not None:
                def copy_content() -> None:
                    # FIXME: Copy Markdown, Copy Text
                    clipboard.put(cpb.TextClipboardContents(str(content)))

                actions.append(('Copy Content', copy_content))

        if not actions:
            return

        self.app.push_screen(
            tx.ActionMenuScreen(
                (event.event.screen_x, event.event.screen_y),
                actions,
            ),
            lambda fn: fn() if fn is not None else None,
        )


#


class StaticMessage(
    OnMountMessageFinalized,
    Message,
    lang.Abstract,
):
    pass
