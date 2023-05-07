import abc
import base64
import datetime
import re
import typing as ta
import uuid

from ... import check
from ... import cron
from ... import lang
from .simple import AutoSerde
from .simple import serde_for
from .types import Serde


T = ta.TypeVar('T')


class BytesSerde(AutoSerde[bytes]):

    def serialize(self, obj: bytes) -> str:
        return base64.b64encode(obj).decode('utf-8')

    def deserialize(self, ser: ta.Any) -> bytes:
        return base64.b64decode(check.isinstance(ser, str).encode('utf-8'))


class _DatetimeSerde(Serde[T], lang.Abstract):

    @abc.abstractproperty
    def formats(self) -> ta.Sequence[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def extract(self, dt: datetime.datetime) -> T:
        raise NotImplementedError

    def serialize(self, obj: T) -> ta.Any:
        return obj.strftime(self.formats[0])

    def deserialize(self, ser: ta.Any) -> T:
        for fmt in self.formats:
            try:
                return self.extract(datetime.datetime.strptime(ser, fmt))
            except ValueError:
                pass
        else:
            raise ValueError(ser)


@serde_for(datetime.date)
class DateSerde(_DatetimeSerde[datetime.date]):

    formats = [
        '%Y-%m-%d',
    ]

    def extract(self, dt: datetime.datetime) -> datetime.date:
        return dt.date()


@serde_for(datetime.time)
class TimeSerde(_DatetimeSerde[datetime.time]):

    formats = [
        '%H:%M:%S.%f',
        '%H:%M:%S',
        '%H:%M',
    ]

    def extract(self, dt: datetime.datetime) -> datetime.time:
        return dt.time()


@serde_for(datetime.datetime)
class DatetimeSerde(_DatetimeSerde[datetime.datetime]):

    formats = [d + 'T' + t for d in DateSerde.formats for t in TimeSerde.formats]

    def extract(self, dt: datetime.datetime) -> T:
        return dt


class UuidSerde(AutoSerde[uuid.UUID]):

    PATTERN = re.compile('([0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12})|([0-9A-Fa-f]{32})')

    def serialize(self, obj: uuid.UUID) -> ta.Any:
        return str(obj)

    def deserialize(self, ser: ta.Any) -> uuid.UUID:
        check.isinstance(ser, str)
        check.arg(self.PATTERN.fullmatch(ser) is not None)
        return uuid.UUID(ser.replace('-', ''))


class CronSpecSerde(AutoSerde[cron.Spec]):

    def serialize(self, obj: cron.Spec) -> ta.Any:
        return str(obj)

    def deserialize(self, ser: ta.Any) -> cron.Spec:
        return cron.Spec.of(ser)
