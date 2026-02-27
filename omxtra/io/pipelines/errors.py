# ruff: noqa: UP006 UP045
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
    @ta.final
    @dc.dataclass(frozen=True)
    class Item:
        direction: ta.Literal['inbound', 'outbound']
        msg: ta.Any

        # _: dc.KW_ONLY

        last_seen: ta.Optional[ta.Any] = None

        def __repr__(self) -> str:
            return (
                f'{self.__class__.__name__}('
                f'{self.direction!r}'
                f', {self.msg!r}' +
                (f', last_seen={self.last_seen!r}' if self.last_seen is not None else '') +
                ')'
            )

    items: ta.Sequence[Item]

    @classmethod
    def new(
            cls,
            *,
            inbound: ta.Optional[ta.Sequence[ta.Any]] = None,
            inbound_with_last_seen: ta.Optional[ta.Sequence[ta.Tuple[ta.Any, ta.Any]]] = None,
            outbound: ta.Optional[ta.Sequence[ta.Any]] = None,
            outbound_with_last_seen: ta.Optional[ta.Sequence[ta.Tuple[ta.Any, ta.Any]]] = None,
    ) -> 'MessageChannelPipelineError':
        items: ta.List[MessageChannelPipelineError.Item] = []
        for msg in inbound or ():
            items.append(MessageChannelPipelineError.Item('inbound', msg))
        for msg, last_seen in inbound_with_last_seen or ():
            items.append(MessageChannelPipelineError.Item('inbound', msg, last_seen=last_seen))
        for msg in outbound or ():
            items.append(MessageChannelPipelineError.Item('outbound', msg))
        for msg, last_seen in outbound_with_last_seen or ():
            items.append(MessageChannelPipelineError.Item('outbound', msg, last_seen=last_seen))
        return cls(items)

    @classmethod
    def new_single(
            cls,
            direction: ta.Literal['inbound', 'outbound'],
            msg: ta.Any,
            *,
            last_seen: ta.Optional[ta.Any] = None,
    ) -> 'MessageChannelPipelineError':
        return cls([
            MessageChannelPipelineError.Item(
                direction,
                msg,
                last_seen=last_seen,
            ),
        ])

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.items!r})'


@dc.dataclass(repr=False)
class MessageNotPropagatedChannelPipelineError(MessageChannelPipelineError, UnhandleableChannelPipelineError):
    pass


@dc.dataclass(repr=False)
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
