"""
TODO:
 - (optionally?) precompute connectivity
  - warn on .. stuff?
 - more specific exceptions
  - collect and dump as a group?
 - 'did not respond' message?
"""
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from .matching import SignalTypeSet
from .matching import SignalTypeSetMatcher
from .signals import ANY_SIGNAL_TYPES
from .signals import AnySignal
from .signals import AnySignalWithSender
from .signals import Signal
from .signals import SignalRequest
from .signals import SignalResponse


T = ta.TypeVar('T')
T2 = ta.TypeVar('T2')


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True, eq=False)
class SignalGraphNode(ta.Generic[T], lang.Final):
    obj: T

    ins: SignalTypeSet
    outs: SignalTypeSet


@dc.dataclass()
class BadSignalGraphNodeOutputError(Exception, ta.Generic[T]):
    obj: T
    output: Signal


class SignalGraph(ta.Generic[T]):
    def __init__(
            self,
            nodes: ta.Iterable[SignalGraphNode[T]],
    ) -> None:
        super().__init__()

        self._nodes_by_obj: ta.Mapping[T, SignalGraph._Node[T]] = col.make_map((
            (n.obj, SignalGraph._Node(n)) for n in nodes
        ), strict=True)

    class _Node(ta.Generic[T2]):
        def __init__(self, node: SignalGraphNode[T2]) -> None:
            self.node = node

            self.ins = SignalTypeSetMatcher(node.ins)
            self.outs = SignalTypeSetMatcher(node.outs)

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class Step(ta.Generic[T2]):
        routed: ta.Mapping[T2, ta.Sequence[AnySignal]]

        req_senders: ta.Mapping[SignalRequest, T2] | None = None

    def next(
            self,
            ins: ta.Iterable[AnySignal | AnySignalWithSender[T]],
            prev_step: Step[T] | None = None,
    ) -> Step[T]:
        routed: dict[T, list[AnySignal | AnySignalWithSender[T]]] = {}

        req_senders: dict[SignalRequest, T] = {}

        for im in ins:
            if isinstance(im, AnySignalWithSender):
                m = im.m

                xn = self._nodes_by_obj[im.x]
                if not xn.outs.matches_obj(m):
                    raise BadSignalGraphNodeOutputError(xn.node.obj, m)

            elif isinstance(im, ANY_SIGNAL_TYPES):
                m = im

            else:
                raise TypeError(im)

            if isinstance(m, SignalResponse):
                n = self._nodes_by_obj[check.not_none(prev_step).req_senders[m.q]]
                if n.ins.matches_obj(m):
                    routed.setdefault(n.node.obj, []).append(m)

            elif isinstance(m, (Signal, SignalRequest)):
                if isinstance(m, SignalRequest):
                    xn = check.isinstance(im, AnySignalWithSender).x
                    req_senders[m] = xn

                for n in self._nodes_by_obj.values():
                    if n.ins.matches_obj(m):
                        routed.setdefault(n.node.obj, []).append(m)

            else:
                raise TypeError(m)

        return SignalGraph.Step(
            routed=routed,

            req_senders=req_senders,
        )
