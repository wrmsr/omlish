"""
TODO:
 - Actor class (final?)
  - knows signal sets
   - still have separate SignalGraph, just gets ref to same signal sets
 - normalize to EmptyActorState, normalize calling conv
  - but keep 'friendly' diff impl conventions
 - disjoint / @dispatch.method-ish Actor - DispatchActor? LOL MethodActor
 - better handle initial states - require nullary ctor somehow? require being a dc?
"""
import abc
import collections.abc
import inspect
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl

from .graphs import SignalGraph
from .graphs import SignalGraphNode
from .matching import build_signal_type_set
from .signals import AnySignal


StatelessActorFn: ta.TypeAlias = ta.Callable[
    [ta.Sequence[AnySignal]],
    ta.Sequence[AnySignal] | ta.Iterator[AnySignal],
]

StatefulActorTupleFn: ta.TypeAlias = ta.Callable[
    ['ActorState', ta.Sequence[AnySignal]],
    tuple['ActorState', ta.Sequence[AnySignal] | ta.Iterator[AnySignal]],
]

StatefulActorGeneratorFn: ta.TypeAlias = ta.Callable[
    ['ActorState', ta.Sequence[AnySignal]],
    ta.Generator[AnySignal, None, 'ActorState'],
]

StatefulActorFn: ta.TypeAlias = ta.Union[
    StatelessActorFn,
    StatefulActorTupleFn,

]

ActorFn: ta.TypeAlias = ta.Union[
    StatelessActorFn,
    StatefulActorFn,
]


##


class ActorState(lang.Abstract):
    pass


##


@dc.dataclass(frozen=True, eq=False)
class Actor(lang.Abstract, lang.Sealed):
    @property
    @abc.abstractmethod
    def fn(self) -> ActorFn:
        raise NotImplementedError


@ta.final
@dc.dataclass(frozen=True, eq=False)
@dc.extra_class_params(repr_id=True)
class StatelessActor(Actor, lang.Final):
    fn: StatelessActorFn = dc.xfield(override=True)


@ta.final
@dc.dataclass(frozen=True, eq=False)
@dc.extra_class_params(repr_id=True)
class StatefulActor(Actor, lang.Final):
    fn: StatefulActorFn = dc.xfield(override=True)
    st_ty: type[ActorState]


##


ActorNode: ta.TypeAlias = SignalGraphNode[Actor]
ActorGraph: ta.TypeAlias = SignalGraph[Actor]


#


_POSITIONAL_PARAM_KINDS = {
    inspect.Parameter.POSITIONAL_ONLY,
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
}


def reflect_actor_node(fn: ta.Callable) -> ActorNode:
    sig = inspect.signature(fn, eval_str=True)

    if len(sig.parameters) == 1:
        [ins_param] = sig.parameters.values()
        check.in_(ins_param.kind, _POSITIONAL_PARAM_KINDS)
        in_ann = ins_param.annotation

        out_ann = check.not_none(sig.return_annotation)

        return ActorNode(
            obj=StatelessActor(fn),

            ins=build_signal_type_set(rfl.type_(in_ann)),
            outs=build_signal_type_set(rfl.type_(out_ann)),
        )

    elif len(sig.parameters) == 2:
        [st_param, ins_param] = sig.parameters.values()

        st_ty = check.issubclass(check.isinstance(st_param.annotation, type), ActorState)

        check.in_(ins_param.kind, _POSITIONAL_PARAM_KINDS)
        in_ann = ins_param.annotation

        out_ann = check.not_none(sig.return_annotation)
        out_rty = rfl.type_(out_ann)
        out_g_rty = check.isinstance(out_rty, rfl.Generic)

        if out_g_rty.cls is tuple:
            check.state(len(out_g_rty.args) == 2)
            out_st_rty, out_rty = out_g_rty.args

            check.is_(out_st_rty, st_ty)

        elif out_g_rty is collections.abc.Generator:
            raise NotImplementedError

        else:
            raise TypeError(out_g_rty)

        return ActorNode(
            obj=StatefulActor(
                fn,
                st_ty,
            ),

            ins=build_signal_type_set(rfl.type_(in_ann)),
            outs=build_signal_type_set(rfl.type_(out_rty)),
        )

    else:
        raise TypeError(fn)
