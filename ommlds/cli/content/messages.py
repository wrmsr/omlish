import abc
import typing as ta

from omlish import check
from omlish import lang

from ... import minichain as mc


##


class MessageContentExtractor(lang.Abstract):
    @abc.abstractmethod
    def extract_message_content(self, message: 'mc.Message') -> ta.Optional['mc.Content']:
        raise NotImplementedError


class MessageContentExtractorImpl(MessageContentExtractor):
    def extract_message_content(self, message: 'mc.Message') -> ta.Optional['mc.Content']:
        if isinstance(message, (mc.SystemMessage, mc.UserMessage, mc.AiMessage)):
            if message.c is not None:
                return check.isinstance(message.c, str)
            else:
                return None

        elif isinstance(message, mc.ToolUseMessage):
            return None

        elif isinstance(message, mc.ToolUseResultMessage):
            return check.isinstance(message.tur.c, str)

        else:
            raise TypeError(message)
