# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


##


class ChannelPipelineError(Exception):
    pass


##


class UnhandleableChannelPipelineError(ChannelPipelineError):
    pass


##
# state


class ContextInvalidatedChannelPipelineError(ChannelPipelineError):
    pass


class SawFinalInputChannelPipelineError(ChannelPipelineError):
    pass


class FinalOutputChannelPipelineError(ChannelPipelineError):
    pass


##
# messages


@dc.dataclass()
class MessageChannelPipelineError(ChannelPipelineError):
    inbound: ta.Optional[ta.Sequence[ta.Any]] = None
    outbound: ta.Optional[ta.Sequence[ta.Any]] = None

    def __repr__(self) -> str:
        return ''.join([
            f'{self.__class__.__name__}(',
            ', '.join([
                *([f'inbound={self.inbound!r}'] if self.inbound is not None else []),
                *([f'outbound={self.outbound!r}'] if self.outbound is not None else []),
            ]),
            ')',
        ])


@dc.dataclass()
class MessageNotPropagatedChannelPipelineError(MessageChannelPipelineError, UnhandleableChannelPipelineError):
    pass


@dc.dataclass()
class MessageReachedTerminalChannelPipelineError(MessageChannelPipelineError, UnhandleableChannelPipelineError):
    pass


##
# misc (TODO: move/cleanup)


class DecodingChannelPipelineError(ChannelPipelineError):
    pass


class IncompleteDecodingChannelPipelineError(DecodingChannelPipelineError):
    pass


class FlowControlValidationChannelPipelineError(ChannelPipelineError):
    pass
