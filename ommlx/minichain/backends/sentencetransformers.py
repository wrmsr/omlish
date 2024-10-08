import typing as ta

from omlish import lang

from ..content import Image
from ..vectors import EmbeddingModel
from ..vectors import EmbeddingRequest
from ..vectors import EmbeddingResponse
from ..vectors import Vector


if ta.TYPE_CHECKING:
    import sentence_transformers as st
else:
    st = lang.proxy_import('sentence_transformers')


class SentencetransformersEmbeddingModel(EmbeddingModel):
    model = 'clip-ViT-B-32'

    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        mdl = st.SentenceTransformer(self.model)

        obj: ta.Any
        v = request.v
        if isinstance(v, str):
            obj = v
        elif isinstance(v, Image):
            obj = v.i
        else:
            raise TypeError(v)

        response = mdl.encode(obj)

        return EmbeddingResponse(v=Vector(response.tolist()))
