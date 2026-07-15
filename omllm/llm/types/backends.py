import abc
import typing as ta

from omcore import lang

from .context import Context
from .messages import AiMessage
from .models import Model
from .options import Options
from .streams import AiStream


##


class Backend(lang.Abstract):
    @property
    @abc.abstractmethod
    def model(self) -> Model:
        raise NotImplementedError


##


class ImmediateBackend(Backend, lang.Abstract):
    @abc.abstractmethod
    def immediate(self, context: Context, options: Options | None = None) -> ta.Awaitable[AiMessage]:
        raise NotImplementedError


##


class StreamBackend(ImmediateBackend, lang.Abstract):
    @abc.abstractmethod
    def stream(self, context: Context, options: Options | None = None) -> ta.Awaitable[AiStream]:
        raise NotImplementedError

    #

    async def immediate(self, context: Context, options: Options | None = None) -> AiMessage:
        async with (await self.stream(context, options)) as it:
            async for _ in it:
                pass
            return it.result.must()
