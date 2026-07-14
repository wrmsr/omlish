import typing as ta

from omlish import dataclasses as dc

from .messages import Message


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class Context:
    system_prompt: str | None = None

    messages: ta.Sequence[Message] = ()
