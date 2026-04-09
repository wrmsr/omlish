# ruff: noqa: UP006 UP037 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


##


class IoPipelineError(Exception):
    pass


##


class UnhandleableIoPipelineError(IoPipelineError):
    pass


##
# state


class StateIoPipelineError(IoPipelineError):
    pass


class ContextInvalidatedIoPipelineError(StateIoPipelineError):
    pass


class SawInitialInputIoPipelineError(StateIoPipelineError):
    pass


class SawFinalInputIoPipelineError(StateIoPipelineError):
    pass


class SawFinalOutputIoPipelineError(StateIoPipelineError):
    pass


##
# messages


@dc.dataclass()
class MessageIoPipelineError(IoPipelineError):
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
    ) -> 'MessageIoPipelineError':
        items: ta.List[MessageIoPipelineError.Item] = []
        for msg in inbound or ():
            items.append(MessageIoPipelineError.Item('inbound', msg))
        for msg, last_seen in inbound_with_last_seen or ():
            items.append(MessageIoPipelineError.Item('inbound', msg, last_seen=last_seen))
        for msg in outbound or ():
            items.append(MessageIoPipelineError.Item('outbound', msg))
        for msg, last_seen in outbound_with_last_seen or ():
            items.append(MessageIoPipelineError.Item('outbound', msg, last_seen=last_seen))
        return cls(items)

    @classmethod
    def new_single(
            cls,
            direction: ta.Literal['inbound', 'outbound'],
            msg: ta.Any,
            *,
            last_seen: ta.Optional[ta.Any] = None,
    ) -> 'MessageIoPipelineError':
        return cls([
            MessageIoPipelineError.Item(
                direction,
                msg,
                last_seen=last_seen,
            ),
        ])

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.items!r})'


@dc.dataclass(repr=False)
class MessageNotPropagatedIoPipelineError(MessageIoPipelineError, UnhandleableIoPipelineError):
    pass


@dc.dataclass(repr=False)
class MessageReachedTerminalIoPipelineError(MessageIoPipelineError, UnhandleableIoPipelineError):
    pass


##
# misc (TODO: move/cleanup)


class DecodingIoPipelineError(IoPipelineError):
    pass


class IncompleteDecodingIoPipelineError(DecodingIoPipelineError):
    pass


class FlowControlValidationIoPipelineError(IoPipelineError):
    pass
