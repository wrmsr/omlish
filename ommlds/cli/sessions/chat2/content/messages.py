import abc

from omlish import check
from omlish import lang

from ..... import minichain as mc


##


class MessageContentExtractor(lang.Abstract):
    @abc.abstractmethod
    def extract_message_content(self, message: mc.Message) -> mc.Content | None:
        raise NotImplementedError


class MessageContentExtractorImpl(MessageContentExtractor):
    def extract_message_content(self, message: mc.Message) -> mc.Content | None:
        if isinstance(message, (mc.SystemMessage, mc.UserMessage, mc.AiMessage)):
            if message.c is not None:
                return check.isinstance(message.c, str)
            else:
                return None

        elif isinstance(message, mc.ToolUseResultMessage):
            return check.isinstance(message.tur.c, str)

        else:
            raise TypeError(message)
