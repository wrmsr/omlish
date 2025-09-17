import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatCompletionTokenLogprob(lang.Final):
    token: str
    bytes: ta.Sequence[int] | None = None
    logprob: float

    @dc.dataclass(frozen=True, kw_only=True)
    class TopLogprob(lang.Final):
        token: str
        bytes: ta.Sequence[int] | None = None
        logprob: float

    top_logprobs: ta.Sequence[TopLogprob]
