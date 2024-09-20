import abc
import typing as ta

from omlish import lang

from .messages import Message


T = ta.TypeVar('T')


##


class MessageParser(abc.ABC, ta.Generic[T]):
    @abc.abstractmethod
    def parse_message(self, msg: Message) -> T:
        raise NotImplementedError


#


class StrMessageParser(MessageParser[str], lang.Final):
    def parse_message(self, msg: Message) -> str:
        return msg.content
