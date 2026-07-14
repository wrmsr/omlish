"""
TODO:
 - caaache lol
  - MethodActor will use same cache machinery, so 'lower' than graph
  - explicitly forbid virtual abc's
 - 'reflect' on correctness of req/resp pair checking
"""
import collections.abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import reflect as rfl

from .signals import AnySignal
from .signals import Signal
from .signals import SignalRequest
from .signals import SignalResponse


SignalTypeTuple: ta.TypeAlias = tuple[type['Signal'], ...]


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class SignalTypeSet:
    tys: SignalTypeTuple

    reqs: ta.Mapping[type[Signal], SignalTypeTuple]
    resps: ta.Mapping[type[Signal], SignalTypeTuple]


def build_signal_type_tuple(sig_tys: ta.Iterable[type]) -> SignalTypeTuple:
    dct = col.make_map((
        ((sig_ty.__qualname__, sig_ty.__module__), check.issubclass(sig_ty, Signal))  # noqa
        for sig_ty in set(sig_tys)
    ), strict=True)

    return tuple(v for k, v in sorted(dct.items(), key=lambda kv: kv[0]))


def unpack_signal_type_or_signal_type_union(rty: rfl.Type) -> set[type[Signal]]:
    if isinstance(rty, type):
        return {check.issubclass(rty, Signal)}  # noqa
    elif isinstance(rty, rfl.Union):
        return {check.issubclass(check.isinstance(e_ty, type), Signal) for e_ty in rty.args}  # noqa
    else:
        raise TypeError(rty)


def build_signal_type_set(ann_rty: rfl.Type) -> SignalTypeSet:
    ann_g_rty = check.isinstance(ann_rty, rfl.Generic)
    check.in_(ann_g_rty.cls, (collections.abc.Sequence, collections.abc.Iterator))
    ann_e_rty = check.single(ann_g_rty.args)

    rtys: set[rfl.Type]
    if isinstance(ann_e_rty, (type, rfl.Generic)):
        rtys = {ann_e_rty}
    elif isinstance(ann_e_rty, rfl.Union):
        rtys = set(ann_e_rty.args)
    else:
        raise TypeError(ann_e_rty)

    tys: set[type] = set()

    reqs: dict[type, set[type]] = {}
    resps: dict[type, set[type]] = {}

    for rty in rtys:
        if isinstance(rty, type):
            tys.add(rty)

        elif isinstance(rty, rfl.Generic):
            if rty.cls is SignalRequest:
                rr_dct = reqs
            elif rty.cls is SignalResponse:
                rr_dct = resps
            else:
                raise TypeError(rty)

            i_rty, o_rty = rty.args
            i_rtys = unpack_signal_type_or_signal_type_union(i_rty)
            o_rtys = unpack_signal_type_or_signal_type_union(o_rty)
            for i_rty in i_rtys:
                rr_dct.setdefault(i_rty, set()).update(o_rtys)

        else:
            raise TypeError(rty)

    return SignalTypeSet(
        tys=build_signal_type_tuple(tys),

        reqs=col.map_values(build_signal_type_tuple, reqs),
        resps=col.map_values(build_signal_type_tuple, resps),
    )


##


class SignalTypeSetMatcher:
    def __init__(self, ts: SignalTypeSet) -> None:
        super().__init__()

        self._ts = ts

    def matches_rty(self, rty: rfl.Type) -> bool:
        if isinstance(rty, type):
            if not issubclass(rty, Signal):
                raise TypeError(rty)

            for ty in self._ts.tys:
                if issubclass(rty, ty):
                    return True

            return False

        elif isinstance(rty, rfl.Generic):
            if rty.cls is SignalRequest:
                dct = self._ts.reqs
            elif rty.cls is SignalResponse:
                dct = self._ts.resps
            else:
                raise TypeError(rty)

            i_arg, o_arg = rty.args
            i_rtys = unpack_signal_type_or_signal_type_union(i_arg)
            o_rtys = unpack_signal_type_or_signal_type_union(o_arg)

            for i_rty in i_rtys:
                for i_ty, o_tys in dct.items():
                    if issubclass(i_rty, i_ty):
                        for o_rty in o_rtys:
                            for o_ty in o_tys:
                                if issubclass(o_rty, o_ty):
                                    return True

            return False

        elif isinstance(rty, rfl.Union):
            for e in rty.args:
                if self.matches_rty(e):
                    return True

            return False

        else:
            raise TypeError(rty)

    def matches_obj(self, o: AnySignal) -> bool:
        if isinstance(o, Signal):
            return isinstance(o, self._ts.tys)

        elif isinstance(o, (SignalRequest, SignalResponse)):
            if o.__class__ is SignalRequest:
                dct = self._ts.reqs
            elif o.__class__ is SignalResponse:
                dct = self._ts.resps
            else:
                raise TypeError(o)

            for i_ty, o_tys in dct.items():
                if isinstance(o.i, i_ty):
                    for o_ty in o_tys:
                        if issubclass(o.O, o_ty):
                            return True

            return False

        else:
            raise TypeError(o)
