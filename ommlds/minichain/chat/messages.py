"""
TODO:
 - channel? reasoning / thinking?
"""
import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ..content.content import Content
from ..metadata import MetadataContainerDataclass
from ..tools.types import ToolUse
from ..tools.types import ToolUseResult
from .metadata import MessageMetadata
from .metadata import MessageMetadatas


MessageT = ta.TypeVar('MessageT', bound='Message')


msh.register_global_module_import('._marshal', __package__)


##


@dc.dataclass(frozen=True)
class Message(MetadataContainerDataclass[MessageMetadatas], lang.Abstract, lang.Sealed):
    _metadata: ta.Sequence[MessageMetadatas] = dc.field(default=(), kw_only=True, repr=False)

    MetadataContainerDataclass._configure_metadata_field(_metadata, MessageMetadatas)  # noqa

    #

    def replace(self, **kwargs: ta.Any) -> ta.Self:
        if (n := dc.replace_is_not(self, **kwargs)) is self:
            return self
        return with_message_original(n, original=self)


Chat: ta.TypeAlias = ta.Sequence[Message]


##
# Notable asymmetry: ContentOriginal is in content.metadata, but this has to be here due to marshaling constraints:
# putting it in chat.metadata requires a `if ta.TYPE_CHECKING` import of Message, which omlish.marshal can't handle.


@dc.dataclass(frozen=True)
class MessageOriginal(MessageMetadata, lang.Final):
    c: ta.Sequence[Message]


def with_message_original(m: MessageT, *, original: Message | ta.Sequence[Message]) -> MessageT:
    if not isinstance(original, ta.Sequence):
        original = [original]
    return m.with_metadata(MessageOriginal(original), discard=[MessageOriginal], override=True)


##


@dc.dataclass(frozen=True)
class AnyUserMessage(Message, lang.Abstract):
    pass


UserChat: ta.TypeAlias = ta.Sequence[AnyUserMessage]


def check_user_chat(chat: Chat) -> UserChat:
    for m in chat:
        check.isinstance(m, AnyUserMessage)
    return ta.cast(UserChat, chat)


#


@dc.dataclass(frozen=True)
class AnyAiMessage(Message, lang.Abstract):
    pass


AiChat: ta.TypeAlias = ta.Sequence[AnyAiMessage]


def check_ai_chat(chat: Chat) -> AiChat:
    for m in chat:
        check.isinstance(m, AnyAiMessage)
    return ta.cast(AiChat, chat)


##


@dc.dataclass(frozen=True)
class SystemMessage(AnyUserMessage, lang.Final):
    c: Content


#


@dc.dataclass(frozen=True)
class DeveloperMessage(AnyUserMessage, lang.Final):
    c: Content


#


@dc.dataclass(frozen=True)
@msh.update_fields_options(['name'], omit_if=operator.not_)
class UserMessage(AnyUserMessage, lang.Final):
    c: Content

    name: str | None = dc.xfield(None, repr_fn=lang.opt_repr)


#


@dc.dataclass(frozen=True)
class AiMessage(AnyAiMessage, lang.Final):
    c: Content = dc.xfield(None, repr_fn=lang.opt_repr)  # TODO: non-null?


#


@dc.dataclass(frozen=True)
class ToolUseMessage(AnyAiMessage, lang.Final):
    tu: ToolUse


@dc.dataclass(frozen=True)
class ToolUseResultMessage(AnyUserMessage, lang.Final):
    tur: ToolUseResult
