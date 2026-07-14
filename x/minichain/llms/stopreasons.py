from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh


##


@msh.set_polymorphic_from_subclasses(naming=msh.Naming.SNAKE, strip_suffix=True)
class StopReason(lang.Abstract, lang.Sealed):
    """
    Why a generation segment stopped. A closed sum (classes-as-ADT), mapped from each backend's vendor finish/stop
    reason. Carried both as a response `StopReasonOutput` (how a backend surfaces it) and, downstream, as a
    `StopReasonMessageMetadata` stamped on the terminal AI message (see `chat.metadata`). A dedicated `StopAiMessage`
    message subtype is the eventual home; this is the interim shape.
    """


@dc.dataclass(frozen=True)
class EndTurnStopReason(StopReason, lang.Final):
    """The model finished its turn naturally (openai `stop`, anthropic `end_turn`, google `STOP`, ...)."""


@dc.dataclass(frozen=True)
class ToolUseStopReason(StopReason, lang.Final):
    """The model stopped to call tools (openai `tool_calls`, anthropic `tool_use`, ...)."""


@dc.dataclass(frozen=True)
class MaxTokensStopReason(StopReason, lang.Final):
    """Generation was truncated by a token limit (openai `length`, anthropic `max_tokens`, google `MAX_TOKENS`)."""


@dc.dataclass(frozen=True)
class StopSequenceStopReason(StopReason, lang.Final):
    """A configured stop sequence was emitted (anthropic `stop_sequence`, openai `stop` with a sequence)."""


@dc.dataclass(frozen=True)
class ContentFilterStopReason(StopReason, lang.Final):
    """Generation was halted by a content filter / safety system."""


@dc.dataclass(frozen=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class OtherStopReason(StopReason, lang.Final):
    """A vendor reason with no current mc mapping; `raw` preserves the original string."""

    raw: str | None = None
