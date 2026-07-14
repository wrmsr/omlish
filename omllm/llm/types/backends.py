import abc
import typing as ta

from omlish import lang

from .context import Context
from .messages import AiMessage
from .options import Options


##


class Backend(lang.Abstract):
    @abc.abstractmethod
    def complete(self, context: Context, options: Options | None = None) -> ta.Awaitable[AiMessage]:
        raise NotImplementedError
