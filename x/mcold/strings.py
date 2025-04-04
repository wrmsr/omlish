import abc
import collections.abc
import typing as ta

from omlish import dataclasses as dc
from omlish import dispatch

from .chat.messages import AiMessage
from .chat.messages import Message
from .chat.messages import SystemMessage
from .chat.messages import ToolExecResultMessage
from .chat.messages import UserMessage
from .content.content import Content
from .content.images import Image
from .content.placeholders import Placeholder
from .services import ServiceRequest


StringTransformable = ta.Union[  # noqa
    str,
    ta.Sequence['StringTransformable'],
    Content,
    Message,
    ServiceRequest,
]

StringTransformableT = ta.TypeVar('StringTransformableT', bound=StringTransformable)


class StringTransform:
    @dispatch.method
    def apply(self, s: StringTransformableT) -> StringTransformableT:
        raise TypeError(s)

    #

    @apply.register
    @abc.abstractmethod
    def apply_str(self, s: str) -> str:
        raise NotImplementedError

    @apply.register
    def apply_sequence(self, s: collections.abc.Sequence) -> collections.abc.Sequence:
        return [self.apply(e) for e in s]

    #

    @apply.register
    def apply_image(self, s: Image) -> Image:
        return s

    @apply.register
    def apply_placeholder(self, s: Placeholder) -> Placeholder:
        return s

    #

    @apply.register
    def apply_ai_message(self, s: AiMessage) -> AiMessage:
        return s

    @apply.register
    def apply_system_message(self, s: SystemMessage) -> SystemMessage:
        return dc.replace(s, s=self.apply(s.s))

    @apply.register
    def apply_tool_exec_result_message(self, s: ToolExecResultMessage) -> ToolExecResultMessage:
        return s

    @apply.register
    def apply_user_message(self, s: UserMessage) -> UserMessage:
        return dc.replace(s, content=self.apply(s.c))

    #

    @apply.register
    def apply_service_request(self, s: ServiceRequest) -> ServiceRequest:
        return dc.replace(s, v=self.apply(s.v))


@dc.dataclass(frozen=True)
class FnStringTransform(StringTransform):
    fn: ta.Callable[[str], str]

    @StringTransform.apply.register  # noqa
    def apply_str(self, s: str) -> str:
        return self.fn(s)


def transform_strings(fn: ta.Callable[[str], str], s: StringTransformableT) -> StringTransformableT:
    return FnStringTransform(fn).apply(s)
