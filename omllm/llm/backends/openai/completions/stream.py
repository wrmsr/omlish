from .....core import StreamSink
from .....core import new_stream
from ....types.backends import StreamBackend
from ....types.content import TextContent
from ....types.context import Context
from ....types.messages import AiMessage
from ....types.options import Options
from ....types.streams import AiEvent
from ....types.streams import AiStream
from ....types.streams import EndAiEvent
from ....types.streams import StartAiEvent
from ..base import BaseBackend
from .requests import RequestPreparer


##


class OpenaiCompletionsStreamBackend(BaseBackend, StreamBackend):
    async def stream(self, context: Context, options: Options | None = None) -> AiStream:
        raw_request = RequestPreparer(  # noqa
            self._model,
            context,
            options,
        ).raw_request()

        raw_request['stream'] = True

        #

        async def inner(sink: StreamSink[AiEvent]) -> AiMessage:
            await sink.emit(StartAiEvent())
            await sink.emit(EndAiEvent())
            return AiMessage([TextContent('FIXME')])

        return await new_stream(inner)
