import typing as ta

from ... import reflect as rfl
from ...funcs import guard as gfs
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory


##


class MultiMarshalerFactory(MarshalerFactory):
    def __init__(
            self,
            *facs: MarshalerFactory,
            strict: bool = False,
    ) -> None:
        super().__init__()

        self._facs = facs
        self._mgf = gfs.multi(*[f.make_marshaler for f in self._facs], strict=strict)

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self._mgf(ctx, rty)


class MultiUnmarshalerFactory(UnmarshalerFactory):
    def __init__(
            self,
            *facs: UnmarshalerFactory,
            strict: bool = False,
    ) -> None:
        super().__init__()

        self._facs = facs
        self._mgf = gfs.multi(*[f.make_unmarshaler for f in self._facs], strict=strict)

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self._mgf(ctx, rty)
