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
            raw_request[self._compat.max_tokens_field or 'max_completion_tokens'] = self._options.max_tokens

        #

        raw_messages: list[dict] = []

        if self._context.system_prompt:
            raw_messages.append({
                'role': 'system',
                'content': self._context.system_prompt,
            })

        for msg in self._context.messages:
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

        if self._context.tools:
            raw_tools: list[dict] = []

            for tool in self._context.tools:
                raw_properties: dict = {}
                raw_required: list[str] = []
                for param in tool.params or []:
                    raw_properties[param.name] = {
                        **({'type': param.type} if param.type else {}),
                        **({'description': param.description} if param.description else {}),
                    }
                    if not param.optional:
                        raw_required.append(param.name)

                raw_tools.append({
                    'type': 'function',
                    'function': {
                        'name': tool.name,
                        **({'description': tool.description} if tool.description else {}),
                        'parameters': {
                            'type': 'object',
                            **({'properties': raw_properties} if raw_properties else {}),
                            **({'required': raw_required} if raw_required else {}),
                        },
                    },
                })

            raw_request['tools'] = raw_tools

        #

        return raw_request
