# @omlish-lite
import dataclasses as dc
import typing as ta


##


class ChannelPipelineError(Exception):
    pass


class IncompleteDecodingChannelPipelineError(ChannelPipelineError):
    pass


class FlowControlValidationChannelPipelineError(ChannelPipelineError):
    pass


class SawEofChannelPipelineError(ChannelPipelineError):
    pass


class ClosedChannelPipelineError(ChannelPipelineError):
    pass


@dc.dataclass()
class MessageNotPropagatedChannelPipelineError(ChannelPipelineError):
    msgs: ta.Sequence[ta.Any]
