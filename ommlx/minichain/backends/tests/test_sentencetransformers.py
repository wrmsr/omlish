import pytest

from omlish.testing import pytest as ptu

from ..sentencetransformers import SentencetransformersEmbeddingService


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('transformers')
def test_sentencetransformers_embedding():
    mdl = SentencetransformersEmbeddingService()
    e = mdl('hi')
    print(e)
