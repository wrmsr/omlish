import inspect
import typing as ta

from omlish import collections as col
from omlish import lang

from .messages import AiMessage
from .messages import AnyAiMessage
from .messages import AnyUserMessage
from .messages import Message
from .messages import SystemMessage
from .messages import ToolUseMessage
from .messages import ToolUseResultMessage
from .messages import UserMessage


C = ta.TypeVar('C')
R = ta.TypeVar('R')


##


class MessageVisitor(lang.Abstract, ta.Generic[C, R]):
    _visit_method_map: ta.ClassVar[ta.Mapping[ta.Any, str]]

    def visit(self, m: Message, ctx: C) -> R:
        try:
            a = self._visit_method_map[type(m)]
        except KeyError:
            raise TypeError(m) from None

        return getattr(self, a)(m, ctx)

    ##
    # per-type visit methods

    def visit_message(self, m: Message, ctx: C) -> R:
        raise TypeError(m)

    ##
    # user messages

    def visit_any_user_message(self, m: AnyUserMessage, ctx: C) -> R:
        return self.visit_message(m, ctx)

    def visit_user_message(self, m: UserMessage, ctx: C) -> R:
        return self.visit_any_user_message(m, ctx)

    def visit_system_message(self, m: SystemMessage, ctx: C) -> R:
        return self.visit_any_user_message(m, ctx)

    def visit_tool_use_result_message(self, m: ToolUseResultMessage, ctx: C) -> R:
        return self.visit_any_user_message(m, ctx)

    ##
    # ai messages

    def visit_any_ai_message(self, m: AnyAiMessage, ctx: C) -> R:
        return self.visit_message(m, ctx)

    def visit_ai_message(self, m: AiMessage, ctx: C) -> R:
        return self.visit_any_ai_message(m, ctx)

    def visit_tool_use_message(self, m: ToolUseMessage, ctx: C) -> R:
        return self.visit_any_ai_message(m, ctx)


MessageVisitor._visit_method_map = col.make_map([  # noqa
    (list(inspect.signature(o).parameters.values())[1].annotation, a)
    for a, o in MessageVisitor.__dict__.items()
    if a.startswith('visit_')
], strict=True)
