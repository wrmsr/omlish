import pytest

from omlish.testing import pytest as ptu

from ....standard import ModelPath
from ..sentence import SentenceTransformersEmbeddingService


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_sentence_transformers_embedding():
    mdl = SentenceTransformersEmbeddingService(
        ModelPath('clip-ViT-B-32'),
    )
    e = mdl('hi')
    print(e)
