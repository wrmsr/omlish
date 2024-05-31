import datetime
import re


def to_seconds(value: datetime.timedelta) -> float:
    return 86400 * value.days + value.seconds + 0.000001 * value.microseconds


def months_ago(date: datetime.date, num: int) -> datetime.date:
    ago_year = date.year
    ago_month = date.month - num
    while ago_month < 1:
        ago_year -= 1
        ago_month += 12
    while ago_month > 12:
        ago_year += 1
        ago_month -= 12
    return datetime.date(ago_year, ago_month, 1)


def parse_date(s: str) -> datetime.date:
    if s.lower() in ['today', 'now']:
        return datetime.date.today()
    elif s.lower() == 'yesterday':
        return datetime.date.today() - datetime.timedelta(days=1)
    elif s.lower().endswith(' days ago'):
        num = int(s.split(' ', 1)[0])
        return datetime.date.today() - datetime.timedelta(days=num)
    elif s.lower().endswith(' months ago'):
        months = int(s.split(' ', 1)[0])
        return months_ago(datetime.date.today(), months)
    else:
        return datetime.date(*map(int, s.split('-', 3)))


_TIMEDELTA_STR_RE = re.compile(
    r'^\s*'
    r'((?P<days>-?\d+)\s*days?,\s*)?'
    r'(?P<hours>\d?\d):(?P<minutes>\d\d)'
    r':(?P<seconds>\d\d+(\.\d+)?)'
    r'\s*$')


_TIMEDELTA_DHMS_RE = re.compile(
    r'^\s*'
    r'(?P<negative>-)?'
    r'((?P<days>\d+(\.\d+)?)\s*(d|days?))?'
    r',?\s*((?P<hours>\d+(\.\d+)?)\s*(h|hours?))?'
    r',?\s*((?P<minutes>\d+(\.\d+)?)\s*(m|minutes?))?'
    r',?\s*((?P<seconds>\d+(\.\d+)?)\s*(s|secs?|seconds?))?'
    r'\s*$')


def parse_timedelta(s: str) -> datetime.timedelta:
    match = _TIMEDELTA_DHMS_RE.match(s)
    if not match:
        match = _TIMEDELTA_STR_RE.match(s)
    if not match:
        raise ValueError
    timedelta_kwargs = {
        k: float(v)
        for k, v in match.groupdict().items()
        if k != 'negative' and v is not None}
    if not timedelta_kwargs:
        raise ValueError()
    sign = -1 if match.groupdict().get('negative') else 1
    return sign * datetime.timedelta(**timedelta_kwargs)
