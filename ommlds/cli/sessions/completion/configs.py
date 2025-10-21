import dataclasses as dc

from .... import minichain as mc


##


DEFAULT_COMPLETION_MODEL_BACKEND = 'openai'


##


@dc.dataclass(frozen=True)
class CompletionConfig:
    content: 'mc.Content'

    _: dc.KW_ONLY

    backend: str | None = None
