import dataclasses as dc
import typing as ta

from omlish.formats import json

from ... import minichain as mc
from ...minichain.backends.openai.embedding import OpenaiEmbeddingService
from ...minichain.backends.transformers.sentence import SentenceTransformersEmbeddingService
from .base import Session


##


DEFAULT_EMBEDDING_MODEL_BACKEND = 'openai'

EMBEDDING_MODEL_BACKENDS: ta.Mapping[str, type[mc.EmbeddingService]] = {
    'openai': OpenaiEmbeddingService,
    'stfm': SentenceTransformersEmbeddingService,
}


##


class EmbeddingSession(Session['EmbeddingSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config):
        content: mc.Content

        _: dc.KW_ONLY

        backend: str | None = None

    def __init__(self, config: Config) -> None:
        super().__init__(config)

    def run(self) -> None:
        mdl = EMBEDDING_MODEL_BACKENDS[self._config.backend or DEFAULT_EMBEDDING_MODEL_BACKEND]()
        response = mdl.invoke(mc.EmbeddingRequest.new(self._config.content))
        print(json.dumps_compact(response.vector))
