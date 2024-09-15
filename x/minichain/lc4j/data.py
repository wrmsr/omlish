import abc
import dataclasses as dc
import enum

from omlish import lang


#


class Content(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class Text(Content, lang.Final):
    s: str


#


class Message(lang.Abstract, lang.Sealed):
    pass


class SystemMessage(Message, lang.Final):
    pass


class UserMessage(Message, lang.Final):
    pass


class AssistantMessage(Message, lang.Final):
    pass


class ToolExecutionResultMessage(Message, lang.Final):
    pass
