from omcore import check
from omcore.formats.json import all as json
from omcore.http import all as http
from omcore.secrets import all as sec

from ....types.backends import ImmediateBackend
from ....types.content import TextContent
from ....types.context import Context
from ....types.messages import AiMessage
from ....types.messages import UserMessage
from ....types.models import Model
from ....types.options import Options


##


class AnthropicMessagesImmediateBackend(ImmediateBackend):
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

    async def immediate(self, context: Context, options: Options | None = None) -> AiMessage:
        effective_options = Options().merge(
            self._model.default_options,
            options,
        )

        #

        raw_request: dict = {
            'model': self._model.key.id,
        }

        if effective_options.max_tokens is not None:
            raw_request['max_tokens'] = effective_options.max_tokens

        #

        raw_messages: list[dict] = []

        if context.system_prompt:
            raw_request['system'] = [{
                'type': 'text',
                'text': context.system_prompt,
            }]

        for msg in context.messages:
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

        http_headers = {
            **({'x-api-key': self._api_key.reveal()} if self._api_key is not None else {}),
            'content-type': 'application/json',
            'accept': 'application/json',
            **(self._model_http.extra_headers or {}),
        }

        http_request = http.HttpClientRequest(
            self._base_url + '/messages',
            headers=http_headers,
            data=json.dumps(raw_request).encode('utf-8'),
        )

        http_response = await http.async_request(
            http_request,
            client=self._http_client,
        )

        if http_response.status != 200:
            err_http_response = await http.async_read_http_client_response(http_response)
            raise http.StatusHttpClientError(err_http_response)

        raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        #

        check.equal(raw_response['type'], 'message')
        check.equal(raw_response['role'], 'assistant')

        response_content: list[TextContent] = []

        for raw_c in raw_response['content']:
            if raw_c['type'] == 'text':
                response_content.append(TextContent(raw_c['text']))

            else:
                raise ValueError(raw_c['type'])

        return AiMessage(
            response_content,
        )
