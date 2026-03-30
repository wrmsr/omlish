import abc
import typing as ta

from omlish import lang

from ...transform.general import CompositeGeneralTransform
from ...transform.general import FnGeneralTransform
from ...transform.general import GeneralTransform
from ...transform.general import TypeFilteredGeneralTransform
from ..messages import Message


##


class MessageTransform(GeneralTransform[Message], lang.Abstract):
    @abc.abstractmethod
    def transform(self, m: Message) -> ta.Sequence[Message]:
        raise NotImplementedError


##


class CompositeMessageTransform(CompositeGeneralTransform[Message], MessageTransform):
    pass


class FnMessageTransform(FnGeneralTransform[Message], MessageTransform):
    pass


class TypeFilteredMessageTransform(TypeFilteredGeneralTransform[Message], MessageTransform):
    pass
