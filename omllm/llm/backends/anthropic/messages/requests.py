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

        self._model = model
        self._context = context
        self._given_options = options

        self._options = Options().merge(
            model.default_options,
            options,
        )

        if model.compat is not None:
            self._compat = check.isinstance(model.compat, OpenaiCompat)
        else:
            self._compat = OpenaiCompat()

    @lang.cached_function
    def raw_request(self) -> dict[str, ta.Any]:
        raw_request: dict = {
            'model': self._model.key.id,
        }

        if self._options.max_tokens is not None:
            raw_request['max_tokens'] = self._options.max_tokens

        #

        raw_messages: list[dict] = []

        if self._context.system_prompt:
            raw_request['system'] = [{
                'type': 'text',
                'text': self._context.system_prompt,
            }]

        for msg in self._context.messages or []:
            if isinstance(msg, UserMessage):
                if isinstance(msg.content, str):
                    raw_messages.append({
                        'role': 'user',
                        'content': msg.content,
                    })

                elif isinstance(msg.content, TextContent):
                    raw_messages.append({
                        'role': 'user',
                        'content': msg.content.text,
                    })

                else:
                    raise TypeError(msg)

            elif isinstance(msg, AiMessage):
                text_parts: list[str] = []

                for c in msg.content:
                    if isinstance(c, TextContent):
                        text_parts.append(c.text)

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
