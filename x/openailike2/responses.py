import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True, kw_only=True)
class Usage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


##


@dc.dataclass(frozen=True, kw_only=True)
class TopLogprob:
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class Logprob[
    TopLogprobT: TopLogprob = TopLogprob,
]:
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None
    top_logprobs: ta.Sequence[TopLogprobT] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class Logprobs[
    LogprobT: Logprob = Logprob,
]:
    content: ta.Sequence[LogprobT] | None = None
    refusal: ta.Sequence[LogprobT] | None = None
