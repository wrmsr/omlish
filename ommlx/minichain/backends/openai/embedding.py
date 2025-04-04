import os

from omlish import check
from omlish.formats import json
from omlish.http import all as http
from omlish.secrets.secrets import Secret

from ...vectors.embeddings import EmbeddingRequest
from ...vectors.embeddings import EmbeddingResponse
from ...vectors.embeddings import EmbeddingService
from ...vectors.vectors import Vector


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='openai', type='EmbeddingService')
class OpenaiEmbeddingService(EmbeddingService):
    model = 'text-embedding-3-small'

    def __init__(
            self,
            *,
            api_key: Secret | str | None = None,
    ) -> None:
        super().__init__()
        self._api_key = Secret.of(api_key if api_key is not None else os.environ['OPENAI_API_KEY'])

    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raw_request = dict(
            model=self.model,
            input=check.isinstance(request.content, str),
        )

        raw_response = http.request(
            'https://api.openai.com/v1/embeddings',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        response = json.loads(check.not_none(raw_response.data).decode('utf-8'))

        return EmbeddingResponse(Vector(response['data'][0]['embedding']))
