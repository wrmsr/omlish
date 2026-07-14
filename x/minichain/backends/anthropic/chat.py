"""
https://docs.claude.com/en/api/messages
https://github.com/anthropics/anthropic-sdk-python/tree/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/types
https://github.com/anthropics/anthropic-sdk-python/blob/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/resources/messages.py#L70
"""
import typing as ta

from omcore import check
from omcore import lang
from omcore import marshal as msh
from omcore import typedvalues as tv
from omcore.formats.json import all as json
from omcore.http import all as http

from ....backends.anthropic.protocol import types as pt
from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.types import ChatChoicesStreamOption
from ...chat.tools.types import Tool
from ...events.types import EventCallback
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceResponseEvent
from ...http.stream import HttpStreamResponseError
from ...llms.types import MaxTokens
from ...llms.types import Temperature
from ...models.configs import ModelName
from ...resources import ResourcesOption
from ...services import StreamOption
from ...standard import ApiKey
from ...types import Option
from .names import MODEL_NAMES
from .protocol import build_ant_request_messages
from .protocol import build_ant_request_tool
from .protocol import build_mc_choices_response


##


class AnthropicChatChoicesServiceBase(lang.Abstract):
    """Shared config consumption, header assembly, and request building for the anthropic Messages backend."""

    URL: ta.ClassVar[str] = 'https://api.anthropic.com/v1/messages'
    API_KEY_ENV: ta.ClassVar[str] = 'ANTHROPIC_API_KEY'
    ANTHROPIC_VERSION: ta.ClassVar[bytes] = b'2023-06-01'

    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(MODEL_NAMES.default))

    # Anthropic requires max_tokens; the api has no default, so the backend supplies one (overridable per request).
    DEFAULT_OPTIONS: ta.ClassVar[tv.TypedValues[Option]] = tv.TypedValues[Option](
        MaxTokens(4096),
    )

    def __init__(
            self,
            # Deliberately the specific consumable union, not bare Config - spec resolution introspects it.
            *configs: ApiKey | ModelName,
            http_client: http.AsyncHttpClient | None = None,
            on_event: EventCallback | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client
        self._on_event = on_event

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)
            self._api_key = check.not_none(ApiKey.pop_secret(cc, env=self.API_KEY_ENV))

    #

    def _build_headers(self) -> dict[ta.Any, ta.Any]:
        return {
            http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
            b'x-api-key': self._api_key.reveal().encode('utf-8'),
            b'anthropic-version': self.ANTHROPIC_VERSION,
        }

    def _build_request(
            self,
            request: ChatChoicesRequest | ChatChoicesStreamRequest,
            *,
            stream: bool = False,
    ) -> pt.MessagesRequest:
        messages, system = build_ant_request_messages(request.v)

        kwargs: dict[str, ta.Any] = {}
        tools: list[pt.ToolSpec] = []

        with tv.consume(
                *self.DEFAULT_OPTIONS,
                *[
                    o
                    for o in request.options
                    if not isinstance(o, (ChatChoicesStreamOption, StreamOption, ResourcesOption))
                ],
                override=True,
        ) as oc:
            kwargs.update(oc.pop_scalar_kwargs(
                temperature=Temperature,
                max_tokens=MaxTokens,
            ))

            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(build_ant_request_tool(t))

        return pt.MessagesRequest(
            model=MODEL_NAMES.resolve(self._model_name.v),
            system=system,
            messages=messages,
            tools=tools or None,
            stream=stream or None,
            **kwargs,
        )


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='anthropic',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class AnthropicChatChoicesService(AnthropicChatChoicesServiceBase):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        a_req = self._build_request(request)

        raw_request = msh.marshal(a_req)

        if self._on_event is not None:
            await self._on_event(ExternalServiceRequestEvent(
                service=self,
                request=raw_request,
            ))

        http_response = await http.async_request(
            self.URL,
            headers=self._build_headers(),
            data=json.dumps(raw_request).encode('utf-8'),
            client=self._http_client,
        )

        if http_response.status != 200:
            raise HttpStreamResponseError(http_response, data=http_response.data)

        raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceResponseEvent(
                service=self,
                response=raw_response,
            ))

        return build_mc_choices_response(msh.unmarshal(raw_response, pt.MessageWithTypeTag))
