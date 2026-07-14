import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .._common import _set_class_marshal_options


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ChatCompletionTokenLogprob(lang.Final):
    token: str
    bytes: ta.Sequence[int] | None = None
    logprob: float

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class TopLogprob(lang.Final):
        token: str
        bytes: ta.Sequence[int] | None = None
        logprob: float

    top_logprobs: ta.Sequence[TopLogprob]
