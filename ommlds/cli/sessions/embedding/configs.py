import dataclasses as dc

from .... import minichain as mc


##


DEFAULT_EMBEDDING_MODEL_BACKEND = 'openai'


##


@dc.dataclass(frozen=True)
class EmbeddingConfig:
    content: 'mc.Content'

    _: dc.KW_ONLY

    backend: str | None = None
