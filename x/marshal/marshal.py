"""
TODO:
 -
"""
import abc
import dataclasses as dc
import threading
import typing as ta

from .specs import Spec
from .values import Value


#




#


@dc.dataclass(frozen=True)
class SetType(RegistryItem):
    marshaler: 'Marshaler'



#


class Manager:
    pass


Marshaler = ta.Callable[['MarshalContext', ta.Any], Value]
MarshalerFactory = Factory['MarshalContext', Spec, Marshaler]


class MarshalContext:
    def make(self, ty: Spec) -> Marshaler:
        raise NotImplementedError
