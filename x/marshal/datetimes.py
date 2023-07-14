import dataclasses as dc
import datetime
import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .specs import Spec
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
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if spec is datetime.datetime:
            return DatetimeMarshaler(DATETIME_FORMATS[0])
        return None
