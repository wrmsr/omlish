import typing as ta

from omlish import check
from omlish import lang

from ...vectors import EmbeddingModel
from ...vectors import EmbeddingRequest
from ...vectors import EmbeddingResponse
from ...vectors import Vector


if ta.TYPE_CHECKING:
    import openai
else:
    openai = lang.proxy_import('openai')


class OpenaiEmbeddingModel(EmbeddingModel):
    model = 'text-embedding-3-small'

    def __init__(self, *, api_key: str | None = None) -> None:
        super().__init__()
        self._api_key = api_key

    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        client = openai.OpenAI(
            api_key=self._api_key,
        )

        response = client.embeddings.create(
            model=self.model,
            input=check.isinstance(request.v, str),
        )

        return EmbeddingResponse(v=Vector(response.data[0].embedding))
