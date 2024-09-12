import typing as ta

from omlish import dataclasses as dc

from .types import Body
from .types import Headers
from .types import NOT_GIVEN
from .types import NotGiven
from .types import Query


##


@dc.dataclass(frozen=True)
class EmbeddingRequest:
    input: str | ta.Sequence[str] | ta.Iterable[int] | ta.Iterable[ta.Iterable[int]]
    model: str
    dimensions: int | NotGiven = NOT_GIVEN
    encoding_format: ta.Literal['float', 'base64'] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | None | NotGiven = NOT_GIVEN


##


@dc.dataclass(frozen=True)
class Embedding:
    embedding: ta.Sequence[float]
    index: int
    object: ta.Literal['embedding']


@dc.dataclass(frozen=True)
class Usage:
    prompt_tokens: int
    total_tokens: int


@dc.dataclass(frozen=True)
class EmbeddingResponse:
    data: ta.Sequence[Embedding]
    model: str
    object: ta.Literal['list']
    usage: Usage


##


def _main() -> None:
    import openai
    openai.embeddings.create  # noqa
