import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import Chat
from ...content.content import Content
from ...content.placeholders import PlaceholderContents


##


@dc.dataclass(frozen=True)
class ProvidedSystemMessage:
    c: Content

    _: dc.KW_ONLY

    priority: int | None = None


class SystemMessageProvider(lang.Abstract):
    @abc.abstractmethod
    def provide_system_messages(self) -> ta.Awaitable[ta.Sequence[ProvidedSystemMessage]]:
        raise NotImplementedError


SystemMessageProviders = ta.NewType('SystemMessageProviders', ta.Sequence[SystemMessageProvider])


##


class PlaceholderContentsProvider(lang.Abstract):
    @abc.abstractmethod
    def provide_placeholder_contents(self) -> ta.Awaitable[PlaceholderContents]:
        raise NotImplementedError


PlaceholderContentsProviders = ta.NewType('PlaceholderContentsProviders', ta.Sequence[PlaceholderContentsProvider])


##


class ChatPreparer(lang.Abstract):
    @abc.abstractmethod
    def prepare_chat(self, chat: Chat) -> ta.Awaitable[Chat]:
        raise NotImplementedError
