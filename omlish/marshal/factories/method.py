import typing as ta

from ... import lang
from ... import reflect as rfl
from ...funcs import guard as gfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory


##


class MarshalerFactoryMethodClass(MarshalerFactory, lang.Abstract):
    @ta.final
    @gfs.method(instance_cache=True)
    def make_marshaler(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        raise NotImplementedError


class UnmarshalerFactoryMethodClass(UnmarshalerFactory, lang.Abstract):
    @ta.final
    @gfs.method(instance_cache=True)
    def make_unmarshaler(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        raise NotImplementedError
