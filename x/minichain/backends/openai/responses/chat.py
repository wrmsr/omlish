"""https://platform.openai.com/docs/api-reference/responses"""
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats.json import all as json
from omlish.http import all as http

from .....backends.openai.protocol import responses as pt
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.stream.choices.types import ChatChoicesStreamOption
from ....chat.tools.types import Tool
from ....external import ExternalServiceRequestEvent
from ....external import ExternalServiceResponseEvent
from ....http.stream import HttpStreamResponseError
from ....llms.types import MaxTokens
from ....llms.types import Temperature
from ....resources import ResourcesOption
from ....services import StreamOption
from ..compat import OpenaiCompatChatChoicesServiceBase
from .protocol import build_mc_choices_response
from .protocol import build_rsp_input_items
from .protocol import build_rsp_request_tool


##


class OpenaiResponsesServiceBase(OpenaiCompatChatChoicesServiceBase, lang.Abstract):
    """
    Not an openai-compat *dialect* service - the Responses api is its own wire format - but it shares the dialect
    base's config consumption and auth/header machinery.
    """

    URL: ta.ClassVar[str] = 'https://api.openai.com/v1/responses'

    def _build_rsp_request(
            self,
            request: ChatChoicesRequest | ta.Any,
            *,
            stream: bool = False,
    ) -> pt.ResponsesRequest:
        kwargs: dict[str, ta.Any] = {}
        tools: list[pt.ResponsesTool] = []

        with tv.consume(*[
            o
            for o in request.options
            if not isinstance(o, (ChatChoicesStreamOption, StreamOption, ResourcesOption))
        ]) as oc:
            kwargs.update(oc.pop_scalar_kwargs(
                temperature=Temperature,
                max_output_tokens=MaxTokens,
            ))

            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(build_rsp_request_tool(t))

        return pt.ResponsesRequest(
            model=self.MODEL_NAMES.resolve(self._model_name.v),
            input=build_rsp_input_items(request.v),
            tools=tools or None,
            stream=stream or None,
            **kwargs,
        )


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='openai-responses',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class OpenaiResponsesChatChoicesService(OpenaiResponsesServiceBase):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        rsp_request = self._build_rsp_request(request)

        raw_request = msh.marshal(rsp_request)

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

        return build_mc_choices_response(msh.unmarshal(raw_response, pt.ResponsesResponse))
