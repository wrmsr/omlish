import typing as ta

from omlish import lang

from ..content.images import Image
from ..vectors.embeddings import EmbeddingRequest
from ..vectors.embeddings import EmbeddingResponse
from ..vectors.embeddings import EmbeddingService
from ..vectors.vectors import Vector


if ta.TYPE_CHECKING:
    import sentence_transformers as st
else:
    st = lang.proxy_import('sentence_transformers')


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(
#     name='sentencetransformers',
#     aliases=['st'],
#     type='EmbeddingService',
# )
class SentencetransformersEmbeddingService(EmbeddingService):
    model = 'clip-ViT-B-32'

    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        mdl = st.SentenceTransformer(self.model)

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
