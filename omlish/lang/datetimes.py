import datetime


##


ISO_FMT = '%Y-%m-%dT%H:%M:%S%z'
ISO_FMT_US = '%Y-%m-%dT%H:%M:%S.%f%z'

ISO_FMT_NTZ = '%Y-%m-%dT%H:%M:%S'
ISO_FMT_US_NTZ = '%Y-%m-%dT%H:%M:%S.%f'


#


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.UTC)


def utcfromtimestamp(ts: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ts, tz=datetime.UTC)
