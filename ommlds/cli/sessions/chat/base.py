import dataclasses as dc
import typing as ta

from omlish import lang

from .... import minichain as mc
from ..base import Session


##


DEFAULT_CHAT_MODEL_BACKEND = 'openai'


##


ChatOption: ta.TypeAlias = mc.ChatChoicesOptions
ChatOptions = ta.NewType('ChatOptions', ta.Sequence[ChatOption])


##


ChatSessionConfigT = ta.TypeVar('ChatSessionConfigT', bound='ChatSession.Config')


class ChatSession(Session[ChatSessionConfigT], lang.Abstract, ta.Generic[ChatSessionConfigT]):
    @dc.dataclass(frozen=True)
    class Config(Session.Config, lang.Abstract):
        _: dc.KW_ONLY

        markdown: bool = False

        dangerous_no_tool_confirmation: bool = False

    def __init__(
            self,
            config: ChatSessionConfigT,
    ) -> None:
        super().__init__(config)
