import dataclasses as dc

from .json import JsonObject
from .typetags import TypeTagged


##


class Tool(
    TypeTagged,
    type_tag_field='type',
):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class FunctionToolFunction:
    name: str
    description: str | None = None
    parameters: JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionTool[
    FunctionToolFunctionT: FunctionToolFunction = FunctionToolFunction,
](
    Tool,
    type_tag='function',
):
    function: FunctionToolFunctionT


##


class ToolCall(
    TypeTagged,
    type_tag_field='type',
):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class FunctionToolCallFunction:
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionToolCall[
    FunctionToolCallFunctionT: FunctionToolCallFunction = FunctionToolCallFunction,
](
    ToolCall,
    type_tag='function',
):
    id: str
    function: FunctionToolCallFunctionT
