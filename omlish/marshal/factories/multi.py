import typing as ta

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


class MultiMarshalerFactory(MarshalerFactory):
    def __init__(
            self,
            fs: ta.Iterable[MarshalerFactory],
            *,
            strict: bool = False,
    ) -> None:
        super().__init__()

        self._fs = list(fs)
        self._mmf: mfs.MultiMatchFn[[MarshalContext, rfl.Type], Marshaler] = mfs.MultiMatchFn(
            [f.make_marshaler for f in self._fs],
            strict=strict,
        )

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._mmf


class MultiUnmarshalerFactory(UnmarshalerFactory):
    def __init__(
            self,
            fs: ta.Iterable[UnmarshalerFactory],
            *,
            strict: bool = False,
    ) -> None:
        super().__init__()

        self._fs = list(fs)
        self._mmf: mfs.MultiMatchFn[[UnmarshalContext, rfl.Type], Unmarshaler] = mfs.MultiMatchFn(
            [f.make_unmarshaler for f in self._fs],
            strict=strict,
        )

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._mmf
