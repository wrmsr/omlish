import pytest

from omlish import lang

from .....models.configs import ModelPath
from .....services import Request
from ..sentence import SentenceTransformersEmbeddingService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_sentence_transformers_embedding():
    mdl = SentenceTransformersEmbeddingService(
        ModelPath('clip-ViT-B-32'),
    )
    e = lang.sync_await(mdl.invoke(Request('hi')))
    print(e)
