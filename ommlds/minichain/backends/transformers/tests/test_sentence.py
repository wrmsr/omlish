import pytest

from ....services import Request
from ....standard import ModelPath
from ..sentence import SentenceTransformersEmbeddingService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_sentence_transformers_embedding():
    mdl = SentenceTransformersEmbeddingService(
        ModelPath('clip-ViT-B-32'),
    )
    e = mdl.invoke(Request('hi'))
    print(e)
