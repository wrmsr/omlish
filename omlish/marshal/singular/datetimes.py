import dataclasses as dc
import datetime
import typing as ta

from ... import check
from ... import datetimes as dts
from ..base import MarshalContext
from ..base import Marshaler
from ..base import TypeMapMarshalerFactory
from ..base import TypeMapUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..values import Value


DatetimeLikeT = ta.TypeVar('DatetimeLikeT', bound=datetime.datetime | datetime.date | datetime.time)

_DATETIME_LIKES = (
    datetime.datetime,
    datetime.date,
    datetime.time,
)


##


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


##


@dc.dataclass(frozen=True)
class DatetimeMarshaler(Marshaler, ta.Generic[DatetimeLikeT]):
    cls: type[DatetimeLikeT]
    fmt: str

    def marshal(self, ctx: MarshalContext, o: DatetimeLikeT) -> Value:
        return o.strftime(self.fmt)


_ZERO_DATE = datetime.datetime.now().strptime('', '').date()  # noqa
_ZERO_TIME = datetime.time(0)


@dc.dataclass(frozen=True)
class DatetimeUnmarshaler(Unmarshaler, ta.Generic[DatetimeLikeT]):
    cls: type[DatetimeLikeT]
    fmts: ta.Sequence[str]
    try_iso: bool = False

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> DatetimeLikeT:
        v = check.isinstance(v, str)

        if self.try_iso:
            try:
                return self.cls.fromisoformat(v)  # type: ignore
            except ValueError:
                pass

        for fmt in self.fmts:
            try:
                dt = datetime.datetime.strptime(v, fmt)  # FIXME: timezone  # noqa
            except ValueError:
                pass
            else:
                if self.cls is datetime.datetime:
                    return dt  # type: ignore
                elif self.cls is datetime.date:
                    if dt.time() != _ZERO_TIME:
                        raise ValueError(dt)
                    return dt.date()  # type: ignore
                elif self.cls is datetime.time:
                    if dt.date() != _ZERO_DATE:
                        raise ValueError(dt)
                    return dt.time()  # type: ignore
                else:
                    raise TypeError(self.cls)

        raise ValueError(v)


##


class IsoDatetimeMarshalerUnmarshaler(Marshaler, Unmarshaler, ta.Generic[DatetimeLikeT]):
    cls: type[DatetimeLikeT]

    def marshal(self, ctx: MarshalContext, o: DatetimeLikeT) -> Value:
        return o.isoformat()

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> DatetimeLikeT:
        return self.cls.fromisoformat(v)  # type: ignore


##


class TimedeltaMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: datetime.timedelta) -> Value:
        return str(o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return dts.parse_timedelta(check.isinstance(v, str))


##


DATETIME_MARSHALER_FACTORY = TypeMapMarshalerFactory({
    **{cls: DatetimeMarshaler(cls, DATETIME_FORMATS[0]) for cls in _DATETIME_LIKES},
    datetime.timedelta: TimedeltaMarshalerUnmarshaler(),
})

DATETIME_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({
    **{cls: DatetimeUnmarshaler(cls, DATETIME_FORMATS, try_iso=True) for cls in _DATETIME_LIKES},
    datetime.timedelta: TimedeltaMarshalerUnmarshaler(),
})
