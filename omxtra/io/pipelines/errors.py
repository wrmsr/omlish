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


class SawFinalInputChannelPipelineError(ChannelPipelineError):
    pass


class FinalOutputdChannelPipelineError(ChannelPipelineError):
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


@dc.dataclass(repr=False)
class MessageNotPropagatedChannelPipelineError(MessageChannelPipelineError):
    pass


@dc.dataclass(repr=False)
class MessageReachedTerminalChannelPipelineError(MessageChannelPipelineError):
    pass


##
# misc (TODO: move/cleanup)


class IncompleteDecodingChannelPipelineError(ChannelPipelineError):
    pass


class FlowControlValidationChannelPipelineError(ChannelPipelineError):
    pass
