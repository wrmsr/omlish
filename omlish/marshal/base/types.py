import abc
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from .values import Value


if ta.TYPE_CHECKING:
    from .contexts import MarshalContext
    from .contexts import UnmarshalContext


##


class Marshaler(lang.Abstract):
    @abc.abstractmethod
    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        raise NotImplementedError


class Unmarshaler(lang.Abstract):
    @abc.abstractmethod
    def unmarshal(self, ctx: 'UnmarshalContext', v: Value) -> ta.Any:
        raise NotImplementedError


##


MarshalerMaker: ta.TypeAlias = mfs.MatchFn[['MarshalContext', rfl.Type], Marshaler]
UnmarshalerMaker: ta.TypeAlias = mfs.MatchFn[['UnmarshalContext', rfl.Type], Unmarshaler]


class MarshalerFactory(lang.Abstract):
    @property
    @abc.abstractmethod
    def make_marshaler(self) -> MarshalerMaker:
        raise NotImplementedError


class UnmarshalerFactory(lang.Abstract):
    @property
    @abc.abstractmethod
    def make_unmarshaler(self) -> UnmarshalerMaker:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class MarshalerFactory_(MarshalerFactory):  # noqa
    fn: MarshalerMaker

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self.fn


@dc.dataclass(frozen=True)
class UnmarshalerFactory_(UnmarshalerFactory):  # noqa
    fn: UnmarshalerMaker

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self.fn
