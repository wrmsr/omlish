# ruff: noqa: FURB188 UP006 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages


##


@dc.dataclass(frozen=True)
class PipelineSseEvent:
    event: ta.Optional[str] = None
    data: str = ''
    id: ta.Optional[str] = None
    retry: ta.Optional[int] = None


##


class PipelineSseDecoder(ChannelPipelineHandler):
    """Consumes lines and emits SseEvent objects; ignores comment lines and handles blank-line termination."""

    def __init__(self) -> None:
        super().__init__()

        self._event: ta.Optional[str] = None
        self._data: ta.List[str] = []
        self._id: ta.Optional[str] = None
        self._retry: ta.Optional[int] = None

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            self._emit_if_any(ctx)
            ctx.feed_in(msg)
            return

        if not isinstance(msg, str):
            ctx.feed_in(msg)
            return

        line = msg

        if line.endswith('\r'):
            line = msg[:-1]

        if line == '':
            self._emit_if_any(ctx)
            return

        if line.startswith(':'):
            return

        if ':' in line:
            field, value = line.split(':', 1)
            if value.startswith(' '):
                value = value[1:]
        else:
            field, value = line, ''

        if field == 'event':
            self._event = value
        elif field == 'data':
            self._data.append(value)
        elif field == 'id':
            self._id = value
        elif field == 'retry':
            try:
                self._retry = int(value)
            except ValueError:
                pass

    def _emit_if_any(self, ctx: ChannelPipelineHandlerContext) -> None:
        if (
                self._event is None and
                not self._data and
                self._id is None and
                self._retry is None
        ):
            return

        ev = PipelineSseEvent(
            event=self._event,
            data='\n'.join(self._data),
            id=self._id,
            retry=self._retry,
        )

        self._event = None
        self._data.clear()
        self._id = None
        self._retry = None

        ctx.feed_in(ev)
