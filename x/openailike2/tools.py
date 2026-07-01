import dataclasses as dc

from .typetags import TypeTagged
from .json import JsonObject


##


class Tool(TypeTagged):
    __type_tag_field__ = 'type'


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
):
    __type_tag__ = 'function'

    function: FunctionToolFunctionT


##


class ToolCall(TypeTagged):
    __type_tag_field__ = 'type'


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
):
    __type_tag__ = 'function'

    id: str
    function: FunctionToolCallFunctionT
