import typing as ta

from ... import lang
from ... import reflect as rfl
from ...funcs import guard as gfs
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


##


class MarshalerFactoryMethodClass(MarshalerFactory, lang.Abstract):
    @gfs.method(instance_cache=True)
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        raise NotImplementedError


class UnmarshalerFactoryMethodClass(UnmarshalerFactory, lang.Abstract):
    @gfs.method(instance_cache=True)
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        raise NotImplementedError
