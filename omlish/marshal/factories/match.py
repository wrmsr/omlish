from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import MarshalerMaker
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..base.types import UnmarshalerMaker


##


class MarshalerFactoryMatchClass(
    MarshalerFactory,
    mfs.MatchFnClass[[MarshalContext, rfl.Type], Marshaler],
    lang.Abstract,
):
    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self  # noqa


class UnmarshalerFactoryMatchClass(
    UnmarshalerFactory,
    mfs.MatchFnClass[[UnmarshalContext, rfl.Type], Unmarshaler],
    lang.Abstract,
):
    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self  # noqa
