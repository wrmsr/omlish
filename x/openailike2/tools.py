import dataclasses as dc
import typing as ta

from .json import JsonObject


##


class Tool:
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class Function:
    name: str
    description: str | None = None
    parameters: JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionTool[
    FunctionT: Function = Function,
](
    Tool,
):
    function: FunctionT
    type: ta.Literal['function'] = 'function'


##


# class ToolChoice:
#     pass
#
#
# ToolChoiceMode: ta.TypeAlias = ta.Literal[
#     'none',
#     'auto',
#     'required',
# ]
#
# ToolChoiceOption: ta.TypeAlias = ta.Union[
#     ToolChoiceMode,
#     ToolChoice,
# ]
#
#
# ##
#
#
# @dc.dataclass(frozen=True, kw_only=True)
# class NamedToolChoiceFunction:
#     name: str
#
#
# @dc.dataclass(frozen=True, kw_only=True)
# class FunctionToolChoice[
#     FunctionT: NamedToolChoiceFunction = NamedToolChoiceFunction,
# ](
#     ToolChoice,
# ):
#     function: FunctionT
#     type: ta.Literal['function'] = 'function'
