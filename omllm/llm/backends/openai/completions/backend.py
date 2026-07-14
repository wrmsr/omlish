from omcore import check
from omcore.formats.json import all as json
from omcore.http import all as http
from omcore.secrets import all as sec

from ....types.backends import Backend
from ....types.content import TextContent
from ....types.context import Context
from ....types.messages import AiMessage
from ....types.messages import UserMessage
from ....types.models import Model
from ....types.options import Options


##


class OpenaiCompletionsBackend(Backend):
    def __init__(
            self,
            model: Model,
            *,
            api_key: sec.Secret | None = None,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._model = model
        self._api_key = api_key
        self._http_client = http_client

        self._model_http = check.not_none(model.http)
        self._base_url = check.non_empty_str(self._model_http.base_url).rstrip('/')

    @property
    def model(self) -> Model:
        return self._model

    async def complete(self, context: Context, options: Options | None = None) -> AiMessage:
        raw_request: dict = {
            'model': self._model.key.id,
        }

        #

        raw_messages: list[dict] = []

        if context.system_prompt:
            raw_messages.append({
                'role': 'system',
                'content': context.system_prompt,
            })

        for msg in context.messages:
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

        http_headers = {
            'authorization': f'Bearer {check.not_none(self._api_key).reveal()}',
            'content-type': 'application/json',
            'accept': 'application/json',
            **(self._model_http.extra_headers or {}),
        }

        #

        http_response = await http.async_request(
            self._base_url + '/chat/completions',
            headers=http_headers,
            data=json.dumps(raw_request).encode('utf-8'),
            client=self._http_client,
        )

        if http_response.status != 200:
            raise http.StatusHttpClientError(http_response)

        raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        #

        check.equal(raw_response['object'], 'chat.completion')

        raw_choice = check.single(raw_response['choices'])

        raw_msg = raw_choice['message']
        check.equal(raw_msg['role'], 'assistant')

        raw_text = check.non_empty_str(raw_msg['content'])

        return AiMessage(
            (TextContent(raw_text),),
        )
