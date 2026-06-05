"""
Timeline item -> textual widget translation: the (only) place the TUI knows what timeline items look like. The
`ChatDriverInterface` consumes a `Timeline` attachment and calls into here; thanks to the convergence invariant there
is exactly one translation - the same items render the same way whether they arrived live or from a window.
"""
import typing as ta

from omdev.tui import textual as tx
from omlish import check

from ...... import minichain as mc
from ..widgets.messages.ai import StaticAiMessage
from ..widgets.messages.ai import StreamAiMessage
from ..widgets.messages.base import Message
from ..widgets.messages.stream import StreamMessage
from ..widgets.messages.thinking import StaticThinkingMessage
from ..widgets.messages.thinking import StreamThinkingMessage
from ..widgets.messages.tools import ToolMessage
from ..widgets.messages.ui import UiMessage
from ..widgets.messages.user import UserMessage


##


def render_item_content_str(c: mc.Content | None) -> str:
    if c is None:
        return ''

    if isinstance(c, str):
        return c

    return mc.render_content_str(c)


##
# Tool cards


_TOOL_MESSAGE_STATES_BY_ITEM_STATE: ta.Mapping[mc.facades.timelines.ToolUseTimelineItemState, ToolMessage.State] = {
    mc.facades.timelines.ToolUseTimelineItemState.STREAMING: ToolMessage.State.STREAMING,
    mc.facades.timelines.ToolUseTimelineItemState.PENDING: ToolMessage.State.PENDING,
    mc.facades.timelines.ToolUseTimelineItemState.RUNNING: ToolMessage.State.RUNNING,
    mc.facades.timelines.ToolUseTimelineItemState.COMPLETE: ToolMessage.State.COMPLETE,
    mc.facades.timelines.ToolUseTimelineItemState.DENIED: ToolMessage.State.DENIED,
    mc.facades.timelines.ToolUseTimelineItemState.FAILED: ToolMessage.State.FAILED,
}


def build_tool_message_contents(
        item: mc.facades.timelines.ToolUseTimelineItem,
) -> tuple[tx.VisualType, tx.VisualType | None, ToolMessage.State]:
    """(outer, inner, state) for a tool card, from its item - used for both creation and update."""

    name = item.use.name if item.use is not None else (item.partial_name or '?')

    outer = tx.Text.assemble(
        (name, 'bold'),
        ('  ', ''),
        (str(item.state.value), 'dim'),
    )

    inner_parts: list[str] = []

    if item.use is not None:
        tr_uit = mc.render_obj_json_ui_text(
            dict(
                id=item.use.id,
                name=item.use.name,
                args=item.use.args,
            ),
            mc.JsonUiTextRendering(
                'pretty',
                five=True,
                multiline_strings=True,
            ),
        )
        inner_parts.append(str(tr_uit))

    elif item.partial_raw_args:
        inner_parts.append(item.partial_raw_args)

    if item.result is not None:
        inner_parts.append(render_item_content_str(item.result.c))

    if item.error is not None:
        inner_parts.append(repr(item.error))

    inner: tx.VisualType | None = '\n\n'.join(inner_parts) if inner_parts else None

    return (outer, inner, _TOOL_MESSAGE_STATES_BY_ITEM_STATE[item.state])


def build_tool_message(item: mc.facades.timelines.ToolUseTimelineItem) -> ToolMessage:
    outer, inner, state = build_tool_message_contents(item)

    return ToolMessage(
        outer,
        inner,
        state,
        message_uuid=item.id,
    )


def update_tool_message(widget: ToolMessage, item: mc.facades.timelines.ToolUseTimelineItem) -> None:
    widget.update_tool(*build_tool_message_contents(item))


##


def stream_message_cls_for_item(item: mc.facades.timelines.TimelineItem) -> type[StreamMessage] | None:
    if isinstance(item, mc.facades.timelines.AiStreamTimelineItem):
        return StreamAiMessage

    if isinstance(item, mc.facades.timelines.ThinkingStreamTimelineItem):
        return StreamThinkingMessage

    return None


def build_item_message(item: mc.facades.timelines.TimelineItem) -> Message | None:
    """The widget for a timeline item, or None for items this frontend does not display."""

    if isinstance(item, mc.facades.timelines.UserMessageTimelineItem):
        return UserMessage(
            tx.Text(render_item_content_str(item.message.c)),
            message_uuid=item.id,
        )

    elif isinstance(item, mc.facades.timelines.AiMessageTimelineItem):
        return StaticAiMessage(
            render_item_content_str(item.message.c),
            markdown=True,
            message_uuid=item.id,
        )

    elif isinstance(item, mc.facades.timelines.ThinkingTimelineItem):
        return StaticThinkingMessage(
            item.message.c,
            message_uuid=item.id,
        )

    elif isinstance(item, mc.facades.timelines.AiStreamTimelineItem):
        return StreamAiMessage(
            render_item_content_str(item.content),
            message_uuid=item.id,
        )

    elif isinstance(item, mc.facades.timelines.ThinkingStreamTimelineItem):
        return StreamThinkingMessage(
            item.text,
            message_uuid=item.id,
        )

    elif isinstance(item, mc.facades.timelines.ToolUseTimelineItem):
        return build_tool_message(item)

    elif isinstance(item, mc.facades.timelines.UiMessageTimelineItem):
        return UiMessage(
            mc.ui_text_to_rich_text(item.text),
            message_uuid=item.id,
        )

    elif isinstance(item, mc.facades.timelines.ErrorTimelineItem):
        return UiMessage(
            tx.Text.assemble(
                ('error: ', 'bold red'),
                (item.message if item.message is not None else repr(item.error), ''),
            ),
            message_uuid=item.id,
        )

    elif isinstance(item, mc.facades.timelines.MessageTimelineItem):
        return UiMessage(
            tx.Text(render_item_content_str(getattr(item.message, 'c', None))),
            message_uuid=item.id,
        )

    else:
        check.state(isinstance(item, mc.facades.timelines.TimelineItem))
        return None
