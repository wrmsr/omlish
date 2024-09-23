import typing as ta

from omlish import lang

from ..content import Content
from ..content import Text
from ..embeddings import EmbeddingModel_
from ..images import Image
from ..models import Request
from ..models import Response
from ..vectors import Vector


if ta.TYPE_CHECKING:
    import sentence_transformers as st
else:
    st = lang.proxy_import('sentence_transformers')


class SentencetransformersEmbeddingModel(EmbeddingModel_):
    model = 'clip-ViT-B-32'

    def generate(self, request: Request[Content]) -> Response[Vector]:
        mdl = st.SentenceTransformer(self.model)

        obj: ta.Any
        v = request.v
        if isinstance(v, Text):
            obj = v.s
        elif isinstance(v, Image):
            obj = v.i
        else:
            raise TypeError(v)

        response = mdl.encode(obj)

        return Response(Vector(response.tolist()))
