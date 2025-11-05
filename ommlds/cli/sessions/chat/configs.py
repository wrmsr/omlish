import dataclasses as dc
import typing as ta

from .... import minichain as mc


##


DEFAULT_CHAT_MODEL_BACKEND = 'openai'


##


@dc.dataclass(frozen=True)
class ChatConfig:
    _: dc.KW_ONLY

    backend: str | None = None
    model_name: str | None = None

    state: ta.Literal['new', 'continue', 'ephemeral'] = 'continue'

    initial_system_content: ta.Optional['mc.Content'] = None
    initial_user_content: ta.Optional['mc.Content'] = None

    interactive: bool = False
    use_readline: bool | ta.Literal['auto'] = 'auto'

    silent: bool = False
    markdown: bool = False

    stream: bool = False

    enable_tools: bool = False
    enabled_tools: ta.AbstractSet[str] | None = None
    dangerous_no_tool_confirmation: bool = False
