import dataclasses as dc

from ommlds import minichain as mc


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
