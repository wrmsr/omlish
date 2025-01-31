import typing as ta

from .... import check
from .... import dataclasses as dc
from ....funcs import pairs as fps
from ..numerics import numerics as nr
from .formats import MessageFormat
from .formats import MessageParamsUnpacker


##


class Message(dc.Case):
    FORMAT: ta.ClassVar[MessageFormat]
    REPLIES: ta.ClassVar[ta.Collection[nr.NumericReply]] = ()


##


def list_pair_params_unpacker(
        kwarg: str,
        key_param: str,
        value_param: str,
) -> MessageParamsUnpacker:
    def forward(params: ta.Mapping[str, str]) -> ta.Mapping[str, ta.Any]:
        out: dict = dict(params)
        ks = out.pop(key_param)
        vs = out.pop(value_param, None)
        if vs is not None:
            out[kwarg] = list(zip(ks, vs, strict=True))
        else:
            out[kwarg] = ks
        return out

    def backward(kwargs: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, str]:
        out: dict = dict(kwargs)
        ts = out.pop(kwarg)
        is_ts = check.single({isinstance(e, tuple) for e in ts})
        if is_ts:
            ks, vs = zip(*ts)
            out[key_param] = ks
            out[value_param] = vs
        else:
            out[key_param] = ts
        return out

    return fps.of(forward, backward)
