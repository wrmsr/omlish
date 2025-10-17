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

    initial_content: mc.Content | None = None
    interactive: bool = False

    silent: bool = False
    markdown: bool = False

    stream: bool = False

    dangerous_no_tool_confirmation: bool = False
