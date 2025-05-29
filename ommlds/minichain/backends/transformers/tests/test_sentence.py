import pytest

from ....standard import ModelPath
from ..sentence import SentenceTransformersEmbeddingService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_sentence_transformers_embedding():
    mdl = SentenceTransformersEmbeddingService(
        ModelPath('clip-ViT-B-32'),
    )
    e = mdl('hi')
    print(e)
