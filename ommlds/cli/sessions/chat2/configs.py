import dataclasses as dc

from .... import minichain as mc


##


DEFAULT_CHAT_MODEL_BACKEND = 'openai'


##


@dc.dataclass(frozen=True)
class ChatConfig:
    _: dc.KW_ONLY

    backend: str | None = None
    model_name: str | None = None

    new: bool = False

    initial_content: mc.Content | None = None

    markdown: bool = False
    stream: bool = False

    dangerous_no_tool_confirmation: bool = False
