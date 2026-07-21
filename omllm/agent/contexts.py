import typing as ta

from omcore import cached
from omcore import collections as col
from omcore import dataclasses as dc
from omcore import lang

from .messages import Message
from .tools import Tool


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class Context:
    system_prompt: str | None = None

    messages: ta.Sequence[Message] | None = None

    tools: ta.Sequence[Tool] | None = None

    @cached.property
    @dc.init
    def tools_by_name(self) -> ta.Mapping[str, Tool]:
        return col.make_map(((t.name, t) for t in self.tools or []), strict=True)
