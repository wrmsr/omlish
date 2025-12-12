import typing as ta

from omlish import check
from omlish import dataclasses as dc

from ..actors import Actor
from ..actors import ActorState
from ..actors import StatelessActor
from ..actors import StatefulActor
from ..actors import ActorFn
from ..actors import reflect_actor_node
from ..graphs import SignalGraph
from ..signals import ANY_SIGNAL_TYPES
from ..signals import AnySignal
from ..signals import AnySignalWithSender
from ..signals import Signal
from ..signals import SignalRequest
from ..signals import SignalResponse


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(repr_id=True)
class Token(Signal):
    pass


@dc.dataclass(frozen=True)
class FooSignal(Signal):
    foo: Signal


@dc.dataclass(frozen=True)
class BarSignal(Signal):
    bar: Signal


@dc.dataclass(frozen=True)
class BazSignal(Signal):
    baz: Signal


def foo_to_baz_actor(messages: ta.Sequence[FooSignal]) -> ta.Sequence[BazSignal]:
    return [BazSignal(m) for m in messages]


def bar_to_baz_actor(messages: ta.Sequence[BarSignal]) -> ta.Sequence[BazSignal]:
    return [BazSignal(m) for m in messages]


def foo_or_bar_to_baz_actor(messages: ta.Sequence[FooSignal | BarSignal]) -> ta.Sequence[BazSignal]:
    return [BazSignal(m) for m in messages]


@dc.dataclass(frozen=True)
class BarfState(ActorState):
    n: int = 0


def baz_to_bar_or_foo_actor(
        state: BarfState,
        messages: ta.Sequence[BazSignal],
) -> tuple[BarfState, ta.Sequence[FooSignal | BarSignal]]:
    print(f'baz_to_bar_or_foo_actor: {state!r}')
    return (
        dc.replace(
            state,  # noqa
            n=state.n + 1
        ),
        [
            BarSignal(m) if i % 2 else FooSignal(m)
            for i, m in enumerate(messages)
        ],
    )


#


@dc.dataclass(frozen=True)
class StartSignal(Signal):
    tok: Token


FooToBarSignalRequest: ta.TypeAlias = SignalRequest[FooSignal, BarSignal]


def foo_requestor(messages: ta.Sequence[ta.Union[
    StartSignal,
    SignalResponse[FooSignal, BarSignal],
]]) -> ta.Iterator[ta.Union[
    SignalRequest[FooSignal, BarSignal],
]]:
    for m in messages:
        if isinstance(m, StartSignal):
            yield FooToBarSignalRequest(FooSignal(m))

        # FIXME: ~obvious~ match stmt lol
        elif isinstance(m, SignalResponse) and isinstance(m.i, FooSignal) and isinstance(m.o, BarSignal):
            print(f'foo_requestor got response: {m}')

        else:
            raise TypeError(m)


def foo_requestor2(messages: ta.Sequence[ta.Union[
    StartSignal,
    SignalResponse[FooSignal, BarSignal],
]]) -> ta.Iterator[ta.Union[
    SignalRequest[FooSignal, BarSignal],
]]:
    for m in messages:
        if isinstance(m, StartSignal):
            yield FooToBarSignalRequest(FooSignal(m))

        # FIXME: ~obvious~ match stmt lol
        elif isinstance(m, SignalResponse) and isinstance(m.i, FooSignal) and isinstance(m.o, BarSignal):
            print(f'foo_requestor2 got response: {m}')

        else:
            raise TypeError(m)


def foo_responder(messages: ta.Sequence[ta.Union[
    SignalRequest[FooSignal, BarSignal],
]]) -> ta.Iterator[ta.Union[
    SignalResponse[FooSignal, BarSignal],
]]:
    for m in messages:
        if isinstance(m, SignalRequest) and isinstance(m.i, FooSignal):
            yield m.respond(BarSignal(m))

        else:
            raise TypeError(m)


###


def _as_seq(seq_or_it: ta.Sequence[T] | ta.Iterator[T]) -> ta.Sequence[T]:
    if isinstance(seq_or_it, ta.Sequence):
        return seq_or_it
    elif isinstance(seq_or_it, ta.Iterator):
        return list(seq_or_it)
    else:
        raise TypeError(seq_or_it)


def _main() -> None:
    actor_fns: list[ActorFn] = [
        foo_to_baz_actor,
        bar_to_baz_actor,

        foo_or_bar_to_baz_actor,
        baz_to_bar_or_foo_actor,

        foo_requestor,
        foo_requestor2,
        foo_responder,
    ]

    actor_nodes = [reflect_actor_node(a) for a in actor_fns]

    actor_graph = SignalGraph[Actor](actor_nodes)

    #

    ins: ta.Sequence[AnySignal | AnySignalWithSender[Actor]] = [
        FooSignal(Token()),
        StartSignal(Token()),
    ]

    prev_step: SignalGraph.Step[Actor] | None = None

    in_states: dict[StatefulActor, ActorState] = {
        an.obj: an.obj.st_ty()
        for an in actor_nodes
        if isinstance(an.obj, StatefulActor)
    }

    #

    for _ in range(8):
        print('=' * 40)
        for m in ins:
            print(m)
        print()

        step = actor_graph.next(ins, prev_step)

        outs: list[AnySignal | AnySignalWithSender[Actor]] = []
        out_states: dict[StatefulActor, ActorState] = dict(in_states)

        for a, a_ins in step.routed.items():
            if isinstance(a, StatelessActor):
                a_outs = _as_seq(a.fn(a_ins))

            elif isinstance(a, StatefulActor):
                a_in_st = in_states[a]
                a_out_st, a_outs_ = a.fn(a_in_st, a_ins)
                a_outs = _as_seq(a_outs_)
                out_states[a] = a_out_st

            else:
                raise TypeError(a)

            for a_out in a_outs:
                check.isinstance(a_out, ANY_SIGNAL_TYPES)
                outs.append(AnySignalWithSender(a_out, a))

        if not outs:
            break

        ins = outs
        prev_step = step
        in_states = out_states


if __name__ == '__main__':
    _main()
