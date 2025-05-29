import typing as ta

import sentence_transformers as stfm

from ...configs import Config
from ...configs import consume_configs
from ...content.images import Image
from ...standard import ModelPath
from ...vectors.embeddings import EmbeddingRequest
from ...vectors.embeddings import EmbeddingResponse
from ...vectors.embeddings import EmbeddingService
from ...vectors.types import Vector


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(
#     name='sentence_transformers',
#     aliases=['stfm'],
#     type='EmbeddingService',
# )
class SentenceTransformersEmbeddingService(EmbeddingService):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'clip-ViT-B-32'
    )

    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
            self._model_path = cc.pop(ModelPath(self.DEFAULT_MODEL))

    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        mdl = stfm.SentenceTransformer(
            self._model_path.v,
        )

        obj: ta.Any
        v = request.content
        if isinstance(v, str):
            obj = v
        elif isinstance(v, Image):
            obj = v.i
        else:
            raise TypeError(v)

        response = mdl.encode(obj)

        return EmbeddingResponse(Vector(response.tolist()))
