import typing as ta

from omcore import check
from omcore import lang

from ....types.compat import OpenaiCompat
from ....types.content import TextContent
from ....types.context import Context
from ....types.messages import AiMessage
from ....types.messages import UserMessage
from ....types.models import Model
from ....types.options import Options


##


class RequestPreparer:
    def __init__(
            self,
            model: Model,
            context: Context,
            options: Options | None = None,
    ) -> None:
        super().__init__()

        self.model = model
        self.context = context
        self.given_options = options

        self.options = Options().merge(
            model.default_options,
            options,
        )

        if model.compat is not None:
            self.compat = check.isinstance(model.compat, OpenaiCompat)
        else:
            self.compat = OpenaiCompat()

    @lang.cached_function
    def raw_request(self) -> dict[str, ta.Any]:
        raw_request: dict = {
            'model': self.model.key.id,
        }

        if self.options.max_tokens is not None:
            raw_request[self.compat.max_tokens_field or 'max_completion_tokens'] = self.options.max_tokens

        #

        raw_messages: list[dict] = []

        if self.context.system_prompt:
            raw_messages.append({
                'role': 'system',
                'content': self.context.system_prompt,
            })

        for msg in self.context.messages:
            if isinstance(msg, UserMessage):
                if isinstance(msg.c, str):
                    raw_messages.append({
                        'role': 'user',
                        'content': msg.c,
                    })

                elif isinstance(msg.c, TextContent):
                    raw_messages.append({
                        'role': 'user',
                        'content': msg.c.s,
                    })

                else:
                    raise TypeError(msg)

            elif isinstance(msg, AiMessage):
                text_parts: list[str] = []

                for c in msg.c:
                    if isinstance(c, TextContent):
                        text_parts.append(c.s)

                    else:
                        raise TypeError(c)

                raw_messages.append({
                    'role': 'assistant',
                    'content': ''.join(text_parts),
                })

            else:
                raise TypeError(msg)

        raw_request['messages'] = raw_messages

        #

        return raw_request
