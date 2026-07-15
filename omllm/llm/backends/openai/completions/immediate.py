import typing as ta

from omcore import check
from omcore.formats.json import all as json
from omcore.http import all as http

from ....types.backends import ImmediateBackend
from ....types.content import Content
from ....types.content import TextContent
from ....types.content import ToolCall
from ....types.context import Context
from ....types.messages import AiMessage
from ....types.options import Options
from ..base import BaseBackend
from .requests import RequestPreparer


##


class OpenaiCompletionsImmediateBackend(BaseBackend, ImmediateBackend):
    async def immediate(self, context: Context, options: Options | None = None) -> AiMessage:
        raw_request = RequestPreparer(
            self._model,
            context,
            options,
        ).raw_request()

        #

        http_headers = {
            **({'authorization': f'Bearer {self._api_key.reveal()}'} if self._api_key is not None else {}),
            'content-type': 'application/json',
            'accept': 'application/json',
            **(self._model_http.extra_headers or {}),
        }

        http_request = http.HttpClientRequest(
            self._base_url + '/chat/completions',
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

        check.equal(raw_response['object'], 'chat.completion')

        raw_choice = check.single(raw_response['choices'])

        raw_msg = raw_choice['message']
        check.equal(raw_msg['role'], 'assistant')

        content: list[Content] = []

        if raw_content := raw_msg.get('content'):
            content.append(TextContent(check.non_empty_str(raw_content)))

        if raw_tool_calls := raw_msg.get('tool_calls'):
            for raw_tool_call in raw_tool_calls:
                check.equal(raw_tool_call['type'], 'function')
                raw_fn = raw_tool_call['function']
                args = json.loads(raw_fn['arguments'])
                content.append(ToolCall(
                    id=check.non_empty_str(raw_tool_call['id']),
                    name=check.non_empty_str(raw_fn['name']),
                    args=check.isinstance(args, ta.Mapping),
                ))

        return AiMessage(
            ta.cast(ta.Any, content),
        )
