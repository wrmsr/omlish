import typing as ta

from omlish import check

from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolExecResultMessage
from ...chat.messages import UserMessage
from ...chat.tools import ToolSpec


##


def _opt_dct_fld(k, v):
    return {k: v} if v else {}


def render_tool_spec(ts: ToolSpec) -> ta.Mapping[str, ta.Any]:
    return dict(
        name=ts.name,

        **_opt_dct_fld('description', ts.desc),

        parameters=dict(
            type='object',
            properties={
                tp.name: {
                    'type': tp.dtype,
                    **_opt_dct_fld('description', tp.desc),
                }
                for tp in ts.params
            },

            required=[tp.name for tp in ts.params if tp.required],
            additionalProperties=False,
        ),
    )


def build_request_message(m: Message) -> ta.Mapping[str, ta.Any]:
    if isinstance(m, SystemMessage):
        return dict(
            role='system',
            content=m.s,
        )

    elif isinstance(m, AiMessage):
        return dict(
            role='assistant',
            content=m.s,
            **(dict(tool_calls=[
                dict(
                    id=te.id,
                    function=dict(
                        arguments=te.args,
                        name=te.spec.name,
                    ),
                    type='function',
                )
                for te in m.tool_exec_requests
            ]) if m.tool_exec_requests else {}),
        )

    elif isinstance(m, UserMessage):
        return dict(
            role='user',
            content=check.isinstance(m.c, str),
        )

    elif isinstance(m, ToolExecResultMessage):
        return dict(
            role='tool',
            tool_call_id=m.id,
            content=m.s,
        )

    else:
        raise TypeError(m)
