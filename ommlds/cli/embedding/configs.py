from omlish import dataclasses as dc

from ... import minichain as mc
from ..backends.configs import BackendConfig
from ..configs import EntrypointConfig


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True, kw_only=True)
class EmbeddingConfig(
    BackendConfig,
    EntrypointConfig,
):
    content: mc.Content

    backend: str | None = None
