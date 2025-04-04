import typing as ta

from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from .types import ChatRequestOption


ToolDtype: ta.TypeAlias = str


##


@dc.dataclass(frozen=True)
class ToolParam(lang.Final):
    name: str
    dtype: ToolDtype

    _: dc.KW_ONLY

    desc: str | None = None
    required: bool = False


@dc.dataclass(frozen=True)
class ToolSpec(lang.Final):
    name: str
    params: ta.Sequence[ToolParam]

    _: dc.KW_ONLY

    desc: str

    @cached.property
    @dc.init
    def params_by_name(self) -> ta.Mapping[str, ToolParam]:
        return col.make_map_by(lambda p: p.name, self.params, strict=True)


@dc.dataclass(frozen=True)
class Tool(ChatRequestOption, lang.Final):
    spec: ToolSpec


@dc.dataclass(frozen=True)
class ToolExecRequest(lang.Final):
    id: str
    spec: ToolSpec
    args: str
