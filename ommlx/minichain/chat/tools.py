import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .options import ChatRequestOption


##


@dc.dataclass(frozen=True)
class Tool(ChatRequestOption, lang.Final):
    spec: 'ToolSpecification'


##


@dc.dataclass(frozen=True)
class ToolParameters(lang.Final):
    type: str
    props: ta.Mapping[str, ta.Mapping[str, ta.Any]]
    req: ta.AbstractSet[str]


@dc.dataclass(frozen=True)
class ToolSpecification(lang.Final):
    name: str
    desc: str
    params: ToolParameters


@dc.dataclass(frozen=True)
class ToolExecutionRequest(lang.Final):
    id: str
    name: str
    args: str
