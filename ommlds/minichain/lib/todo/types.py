"""
TODO:
 - enums lol
  - * with ToolParam-like desc metadata somehow *
"""
import dataclasses as dc
import typing as ta

from omlish import lang

from ...tools.reflect import tool_param_metadata
from ...tools.types import ToolParam
from ...utils import join_human_readable_str_list
from ...utils import str_literal_values


##


TodoStatus: ta.TypeAlias = ta.Literal[
    'pending',
    'in_progress',
    'completed',
    'cancelled',
]

TOOL_STATUSES: ta.Sequence[str] = str_literal_values(TodoStatus)


ToolPriority: ta.TypeAlias = ta.Literal[
    'high',
    'medium',
    'low',
]

TOOL_PRIORITIES: ta.Sequence[str] = str_literal_values(ToolPriority)


@dc.dataclass(frozen=True, kw_only=True)
class TodoItem(lang.Final):
    id: str | None = dc.field(default=None, metadata=tool_param_metadata(
        desc=(
            'A unique identifier for this todo item within the current session. '
            'If this is not provided it will be automatically set to an integer.'
        ),
    ))
    content: str = dc.field(metadata=tool_param_metadata(desc='A brief description of the task.'))
    priority: ToolPriority = dc.field(metadata=tool_param_metadata(
        desc=f'Priority of the task: {join_human_readable_str_list(map(repr, TOOL_PRIORITIES))}.',
    ))

    status: TodoStatus = dc.field(metadata=tool_param_metadata(
        desc=f'Current status of the task: {join_human_readable_str_list(map(repr, TOOL_STATUSES))}.',
    ))


TODO_ITEM_FIELD_DESCS: ta.Mapping[str, str] = {
    f.name: f.metadata[ToolParam].desc
    for f in dc.fields(TodoItem)  # noqa
}
