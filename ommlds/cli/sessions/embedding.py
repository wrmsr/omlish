import dataclasses as dc
import typing as ta

from omlish import lang
from omlish.formats import json

from ... import minichain as mc
from .base import Session


if ta.TYPE_CHECKING:
    from ...minichain.backends.openai import embedding as mc_openai_embedding
    from ...minichain.backends.transformers import sentence as mc_stfm
else:
    mc_openai_embedding = lang.proxy_import('...minichain.backends.openai.embedding', __package__)
    mc_stfm = lang.proxy_import('...minichain.backends.transformers.sentence', __package__)

##


DEFAULT_EMBEDDING_MODEL_BACKEND = 'openai'

EMBEDDING_MODEL_BACKENDS: ta.Mapping[str, ta.Callable[[], type[mc.EmbeddingService]]] = {
    'openai': lambda: mc_openai_embedding.OpenaiEmbeddingService,
    'stfm': lambda: mc_stfm.SentenceTransformersEmbeddingService,
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
        with lang.maybe_managing(
                EMBEDDING_MODEL_BACKENDS[self._config.backend or DEFAULT_EMBEDDING_MODEL_BACKEND]()(),
        ) as mdl:
            response = mdl.invoke(mc.EmbeddingRequest.new(self._config.content))
            print(json.dumps_compact(response.vector))
