from omlish import check
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http

from ....configs import Config
from ....standard import ApiKey
from ....vectors.embeddings import EmbeddingRequest
from ....vectors.embeddings import EmbeddingResponse
from ....vectors.embeddings import static_check_is_embedding_service
from ....vectors.types import Vector


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='openai',
#     type='EmbeddingService',
# )
@static_check_is_embedding_service
class OpenaiEmbeddingService:
    model = 'text-embedding-3-small'

    def __init__(
            self,
            *configs: Config,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._api_key = ApiKey.pop_secret(cc, env='OPENAI_API_KEY')

    async def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raw_request = dict(
            model=self.model,
            input=check.isinstance(request.v, str),
        )

        raw_response = await http.async_request(
            'https://api.openai.com/v1/embeddings',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
            client=self._http_client,
        )

        response = json.loads(check.not_none(raw_response.data).decode('utf-8'))

        return EmbeddingResponse(Vector(response['data'][0]['embedding']))
