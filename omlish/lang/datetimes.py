import datetime


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.UTC)


def utcfromtimestamp(ts: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ts, tz=datetime.UTC)
