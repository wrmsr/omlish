# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


##


class ChannelPipelineError(Exception):
    pass


##
# state


class ContextInvalidatedChannelPipelineError(ChannelPipelineError):
    pass


class SawEofChannelPipelineError(ChannelPipelineError):
    pass


class ClosedChannelPipelineError(ChannelPipelineError):
    pass


##
# messages


@dc.dataclass()
class MessageNotPropagatedChannelPipelineError(ChannelPipelineError):
    inbound: ta.Optional[ta.Sequence[ta.Any]] = None
    outbound: ta.Optional[ta.Sequence[ta.Any]] = None


@dc.dataclass()
class MessageReachedTerminalChannelPipelineError(ChannelPipelineError):
    inbound: ta.Optional[ta.Sequence[ta.Any]] = None
    outbound: ta.Optional[ta.Sequence[ta.Any]] = None


##
# misc (TODO: move/cleanup)


class IncompleteDecodingChannelPipelineError(ChannelPipelineError):
    pass


class FlowControlValidationChannelPipelineError(ChannelPipelineError):
    pass
