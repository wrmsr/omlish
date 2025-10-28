"""
https://docs.mistral.ai/getting-started/models/
"""
import os
import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.types import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import UserMessage


##


# TODO: generalize lol
class TooManyRequestsMistralError(Exception):
    pass


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='mistral',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class MistralChatChoicesService:
    model: ta.ClassVar[str] = 'mistral-medium-2508'

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def __init__(
            self,
            *,
            api_key: str | None = None,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._api_key = api_key
        self._http_client = http_client

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, AiMessage):
            return check.isinstance(m.c, str)

        elif isinstance(m, (UserMessage, SystemMessage)):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    async def invoke(
            self,
            request: ChatChoicesRequest,
    ) -> ChatChoicesResponse:
        if not (key := self._api_key):
            key = os.environ['MISTRAL_API_KEY']

        req_dct = {
            'model': self.model,
            'messages': [
                {
                    'role': self.ROLES_MAP[type(m)],
                    'content': self._get_msg_content(m),
                }
                for m in request.v
            ],
        }

        resp = await http.async_request(
            'https://api.mistral.ai/v1/chat/completions',
            method='POST',
            data=json.dumps_compact(req_dct).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {key}',
            },
            client=self._http_client,
        )

        if resp.status == 429:
            raise TooManyRequestsMistralError

        resp_dct = json.loads(check.not_none(resp.data).decode('utf-8'))

        return ChatChoicesResponse([
            AiChoice([AiMessage(c['message']['content'])])
            for c in resp_dct['choices']
        ])
