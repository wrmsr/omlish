import typing as ta

import sentence_transformers as stfm

from omlish import typedvalues as tv

from ....configs import Config
from ....content.images import ImageContent
from ....models.configs import ModelPath
from ....vectors.embeddings import EmbeddingRequest
from ....vectors.embeddings import EmbeddingResponse
from ....vectors.embeddings import static_check_is_embedding_service
from ....vectors.types import Vector


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='sentence_transformers',
#     aliases=['stfm'],
#     type='EmbeddingService',
# )
@static_check_is_embedding_service
class SentenceTransformersEmbeddingService:
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'clip-ViT-B-32'
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_path = cc.pop(ModelPath(self.DEFAULT_MODEL))

    async def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        mdl = stfm.SentenceTransformer(
            self._model_path.v,
        )

        obj: ta.Any
        v = request.v
        if isinstance(v, str):
            obj = v
        elif isinstance(v, ImageContent):
            obj = v.i
        else:
            raise TypeError(v)

        response = mdl.encode(obj)

        return EmbeddingResponse(Vector(response.tolist()))
