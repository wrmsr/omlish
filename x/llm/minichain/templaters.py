import dataclasses as dc
import typing as ta

from .messages import Message
from .messages import Messages
from .types import StrMap


@dc.dataclass(frozen=True)
class EnvRef:
    key: str


MessageTemplatable: ta.TypeAlias = ta.Union[
    Message,
    ta.Iterable[Message],
    EnvRef,
]


@dc.dataclass(frozen=True)
class MessageTemplater:
    body: ta.Sequence[MessageTemplatable]

    def template_messages(self, env: StrMap) -> Messages:
        out: list[Message] = []
        stk: list[MessageTemplatable] = list(reversed(self.body))
        while stk:
            b = stk.pop()

            if isinstance(b, Message):
                out.append(dc.replace(b, content=b.content.format(**env)))

            elif isinstance(b, ta.Iterable):
                stk.extend(reversed(b))

            elif isinstance(b, EnvRef):
                stk.extend(reversed(env[b.key]))

            else:
                raise TypeError(b)

        return out
