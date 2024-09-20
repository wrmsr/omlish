import typing as ta

from omlish import check
from omlish import lang

from ..content import Content
from ..content import Text
from ..embeddings import Embedding
from ..embeddings import EmbeddingModel_
from ..models import Request
from ..models import Response


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
    import sentence_transformers as st
else:
    pimg = lang.proxy_import('PIL.Image')
    st = lang.proxy_import('sentence_transformers')


class SentencetransformersEmbeddingModel(EmbeddingModel_):
    model = 'clip-ViT-B-32'

    def generate(self, request: Request[Content]) -> Response[Embedding]:
        mdl = st.SentenceTransformer(self.model)

        response = mdl.encode(check.isinstance(request.v, Text).s)

        return Response(Embedding(response.tolist()))
