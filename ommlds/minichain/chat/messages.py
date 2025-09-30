import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ..content.materialize import CanContent
from ..content.transforms.base import ContentTransform
from ..content.types import Content
from ..metadata import MetadataContainer
from ..tools.types import ToolUse
from ..tools.types import ToolUseResult
from .metadata import MessageMetadatas


msh.register_global_module_import('._marshal', __package__)


##


@dc.dataclass(frozen=True)
class Message(  # noqa
    MetadataContainer[MessageMetadatas],
    lang.Abstract,
    lang.Sealed,
):
    _metadata: ta.Sequence[MessageMetadatas] = dc.field(
        default=(),
        kw_only=True,
        repr=False,
        metadata=_tv_field_metadata(
            MessageMetadatas,
            marshal_name='metadata',
        ),
    )

    @property
    def metadata(self) -> tv.TypedValues[MessageMetadatas]:
        return check.isinstance(self._metadata, tv.TypedValues)

    def with_metadata(self, *mds: MessageMetadatas, override: bool = False) -> ta.Self:
        return dc.replace(self, _metadata=tv.TypedValues(*self._metadata, *mds, override=override))


Chat: ta.TypeAlias = ta.Sequence[Message]


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
    c: CanContent


#


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['name'], omit_if=operator.not_)
class UserMessage(AnyUserMessage, lang.Final):
    c: CanContent

    name: str | None = dc.xfield(None, repr_fn=dc.opt_repr)


#


@dc.dataclass(frozen=True)
class AiMessage(AnyAiMessage, lang.Final):
    c: Content = dc.xfield(None, repr_fn=dc.opt_repr)  # TODO: non-null?


#


@dc.dataclass(frozen=True)
class ToolUseMessage(AnyAiMessage, lang.Final):
    tu: ToolUse


@dc.dataclass(frozen=True)
class ToolUseResultMessage(AnyUserMessage, lang.Final):
    tur: ToolUseResult


##


class _MessageContentTransform(ContentTransform, lang.Final, lang.NotInstantiable):
    @dispatch.install_method(ContentTransform.apply)
    def apply_system_message(self, m: SystemMessage) -> SystemMessage:
        return dc.replace(m, c=self.apply(m.c))

    @dispatch.install_method(ContentTransform.apply)
    def apply_user_message(self, m: UserMessage) -> UserMessage:
        return dc.replace(m, c=self.apply(m.c))

    @dispatch.install_method(ContentTransform.apply)
    def apply_ai_message(self, m: AiMessage) -> AiMessage:
        return dc.replace(m, c=self.apply(m.c))

    @dispatch.install_method(ContentTransform.apply)
    def apply_tool_use_message(self, m: ToolUseMessage) -> ToolUseMessage:
        return dc.replace(m, tu=self.apply(m.tu))

    @dispatch.install_method(ContentTransform.apply)
    def apply_tool_use_result_message(self, m: ToolUseResultMessage) -> ToolUseResultMessage:
        return dc.replace(m, tur=self.apply(m.tur))
