from omlish import dataclasses as dc

from .... import minichain as mc
from ..configs import SessionConfig


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True, kw_only=True)
class CompletionConfig(SessionConfig):
    content: 'mc.Content'

    backend: str | None = None
