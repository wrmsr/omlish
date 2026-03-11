"""
TODO:
 - html?
 - terminal?
 - rich? textual.Content?
"""
import abc
import typing as ta

from omlish import lang

from ..... import minichain as mc


##


class ContentPrinting(lang.Abstract):
    @abc.abstractmethod
    def print_content(self, content: 'mc.Content') -> ta.Awaitable[None]:
        raise NotImplementedError


class StreamContentPrinting(lang.Abstract):
    @abc.abstractmethod
    def create_context(self) -> ta.AsyncContextManager[ContentPrinting]:
        raise NotImplementedError
