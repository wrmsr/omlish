import typing as ta

from ... import lang
from ... import reflect as rfl
from ...funcs import guard as gfs
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory


##


class MarshalerFactoryMethodClass(MarshalerFactory, lang.Abstract):
    @gfs.method(instance_cache=True)
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        raise NotImplementedError


class UnmarshalerFactoryMethodClass(UnmarshalerFactory, lang.Abstract):
    @gfs.method(instance_cache=True)
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        raise NotImplementedError
