import abc
import typing as ta

from omcore import lang

from .context import Context
from .messages import AiMessage
from .models import Model
from .options import Options


##


class Backend(lang.Abstract):
    @property
    @abc.abstractmethod
    def model(self) -> Model:
        raise NotImplementedError


class ImmediateBackend(Backend, lang.Abstract):
    @abc.abstractmethod
    def complete(self, context: Context, options: Options | None = None) -> ta.Awaitable[AiMessage]:
        raise NotImplementedError


class StreamBackend(Backend, lang.Abstract):
    pass
