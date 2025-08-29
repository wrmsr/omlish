from ... import lang
from ..base.types import MarshalerFactory
from ..base.types import MarshalerMaker
from ..base.types import UnmarshalerFactory
from ..base.types import UnmarshalerMaker


##


class SimpleMarshalerFactory(
    MarshalerFactory,
    MarshalerMaker,
    lang.Abstract,
):
    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self  # noqa


class SimpleUnmarshalerFactory(
    UnmarshalerFactory,
    UnmarshalerMaker,
    lang.Abstract,
):
    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self  # noqa
