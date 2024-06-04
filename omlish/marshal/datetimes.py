import dataclasses as dc
import datetime
import typing as ta

from .. import check
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .factories import TypeMapFactory
from .values import Value


DATE_FORMATS: ta.Sequence[str] = [
    '%Y-%m-%d',
]

TIME_FORMATS: ta.Sequence[str] = [
    ' '.join([tp, *tz])
    for tp in [
        '%H:%M:%S.%f',
        '%H:%M:%S',
        '%H:%M',
    ]
    for tz in ta.cast(list[list[str]], [
        [],
        ['%z'],
        ['%Z'],
        ['%z', '%Z'],
        ['%Z', '%z'],
    ])
]

SEPS: ta.Sequence[str] = ['T', ' ']

DATETIME_FORMATS: ta.Sequence[str] = [
    s.join([df, tf])
    for s in SEPS
    for df in DATE_FORMATS
    for tf in TIME_FORMATS
]


@dc.dataclass(frozen=True)
class DatetimeMarshaler(Marshaler):
    fmt: str

    def marshal(self, ctx: MarshalContext, o: datetime.datetime) -> Value:
        return o.strftime(self.fmt)


@dc.dataclass(frozen=True)
class DatetimeUnmarshaler(Unmarshaler):
    fmts: ta.Sequence[str]
    try_iso: bool = False

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> datetime.datetime:
        v = check.isinstance(v, str)

        if self.try_iso:
            try:
                return datetime.datetime.fromisoformat(v)
            except ValueError:
                pass

        for fmt in self.fmts:
            try:
                return datetime.datetime.strptime(v, fmt)
            except ValueError:
                pass

        raise ValueError(v)


DATETIME_MARSHALER = DatetimeMarshaler(DATETIME_FORMATS[0])
DATETIME_UNMARSHALER = DatetimeUnmarshaler(DATETIME_FORMATS, try_iso=True)

DATETIME_MARSHALER_FACTORY: MarshalerFactory = TypeMapFactory({datetime.datetime: DATETIME_MARSHALER})
DATETIME_UNMARSHALER_FACTORY: UnmarshalerFactory = TypeMapFactory({datetime.datetime: DATETIME_UNMARSHALER})


class IsoDatetimeMarshalerUnmarshaler(Marshaler, Unmarshaler):

    def marshal(self, ctx: MarshalContext, o: datetime.datetime) -> Value:
        return o.isoformat()

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> datetime.datetime:
        return datetime.datetime.fromisoformat(v)  # type: ignore
