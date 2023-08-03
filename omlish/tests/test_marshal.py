import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang


##


Value = ta.Union[
    None,
    bool,
    int,
    float,
    str,
    bytes,
    list['Value'],
    dict[str, 'Value'],
]


##


class MarshalException(Exception):
    pass


@dc.dataclass(frozen=True)
class MarshalContext(lang.Final):
    """
    Make func(ctx *MarshalContext, ty reflect.Type) (Marshaler, error)
    Opts ctr.Map[reflect.Type, MarshalOpt]
    Reg  *Registry
    """


class Marshaler(lang.Abstract):
    @abc.abstractmethod
    def marshal(self, ctx: MarshalContext, v: ta.Any) -> Value:
        raise NotImplementedError
