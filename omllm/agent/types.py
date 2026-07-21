import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from .. import llm


##


type Message = llm.Message


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class Context:
    system_prompt: str | None = None

    messages: ta.Sequence[Message] | None = None
