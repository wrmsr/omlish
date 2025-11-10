import abc
import typing as ta

from omlish import lang

from ... import minichain as mc


##


class ContentRendering(lang.Abstract):
    @abc.abstractmethod
    def render_content(self, content: 'mc.Content') -> ta.Awaitable[None]:
        raise NotImplementedError


class StreamContentRendering(lang.Abstract):
    @abc.abstractmethod
    def create_context(self) -> ta.AsyncContextManager[ContentRendering]:
        raise NotImplementedError
