import typing as ta

from omlish import dataclasses as dc

from .types import Body
from .types import Headers
from .types import NOT_GIVEN
from .types import NotGiven
from .types import Query


@dc.dataclass(frozen=True)
class Logprobs:
    text_offset: ta.Sequence[int] | None = None
    token_logprobs: ta.Sequence[float] | None = None
    tokens: ta.Sequence[str] | None = None
    top_logprobs: ta.Sequence[ta.Mapping[str, float]] | None = None


@dc.dataclass(frozen=True)
class CompletionChoice:
    finish_reason: ta.Literal['stop', 'length', 'content_filter']
    index: int
    text: str
    logprobs: Logprobs | None = None


@dc.dataclass(frozen=True)
class CompletionUsage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


@dc.dataclass(frozen=True)
class Completion:
    id: str
    choices: ta.Sequence[CompletionChoice]
    created: int
    model: str
    object: ta.Literal['text_completion']
    system_fingerprint: str | None = None
    usage: CompletionUsage | None = None


class StreamOptionsParam(ta.TypedDict, total=False):
    include_usage: bool


@dc.dataclass(frozen=True)
class CompletionRequest:
    model: str
    prompt: str | ta.Sequence[str] | ta.Iterable[int] | ta.Iterable[ta.Iterable[int]] | None
    best_of: int | None | NotGiven = NOT_GIVEN
    echo: bool | None | NotGiven = NOT_GIVEN
    frequency_penalty: float | None | NotGiven = NOT_GIVEN
    logit_bias: ta.Mapping[str, int] | None | NotGiven = NOT_GIVEN
    logprobs: int | None | NotGiven = NOT_GIVEN
    max_tokens: int | None | NotGiven = NOT_GIVEN
    n: int | None | NotGiven = NOT_GIVEN
    presence_penalty: float | None | NotGiven = NOT_GIVEN
    seed: int | None | NotGiven = NOT_GIVEN
    stop: str | ta.Sequence[str] | None | NotGiven = NOT_GIVEN
    stream: bool | None | NotGiven = NOT_GIVEN
    stream_options: StreamOptionsParam | None | NotGiven = NOT_GIVEN
    suffix: str | None | NotGiven = NOT_GIVEN
    temperature: float | None | NotGiven = NOT_GIVEN
    top_p: float | None | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | None | NotGiven = NOT_GIVEN
