import dataclasses as dc
import datetime
import typing as ta

from .. import check
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


DATE_FORMATS = [
    '%Y-%m-%d',
]


TIME_FORMATS = [
    '%H:%M:%S.%f',
    '%H:%M:%S',
    '%H:%M',
]

DATETIME_FORMATS = [
    'T'.join([DATE_FORMATS[0], TIME_FORMATS[0]])
]


@dc.dataclass(frozen=True)
class DatetimeMarshaler(Marshaler):
    fmt: str

    def marshal(self, ctx: MarshalContext, o: datetime.datetime) -> Value:
        return o.strftime(self.fmt)


class DatetimeMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, rty: rfl.Reflected) -> ta.Optional[Marshaler]:
        if rty is datetime.datetime:
            return DatetimeMarshaler(DATETIME_FORMATS[0])
        return None


@dc.dataclass(frozen=True)
class DatetimeUnmarshaler(Unmarshaler):
    fmts: ta.Sequence[str]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> datetime.datetime:
        v = check.isinstance(v, str)
        for fmt in self.fmts:
            try:
                return datetime.datetime.strptime(v, fmt)
            except ValueError:
                pass
        raise ValueError(v)


class DatetimeUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, rty: rfl.Reflected) -> ta.Optional[Unmarshaler]:
        if rty is datetime.datetime:
            return DatetimeUnmarshaler(DATETIME_FORMATS)
        return None
