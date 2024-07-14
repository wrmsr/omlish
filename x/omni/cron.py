"""
https://en.wikipedia.org/wiki/Cron
"""
import typing as ta

from . import check
from . import collections as ocol
from . import dataclasses as dc
from .collections import seq


T = ta.TypeVar('T')


class Enum(dc.Pure, ta.Generic[T]):
    lst: ta.Sequence[T]
    dct: ta.Mapping[T, int]


def _enum(l: ta.Sequence[T]) -> Enum[T]:
    return Enum(ocol.frozenlist(l), ocol.frozendict(map(reversed, enumerate(l))))


MONTHS = _enum([
    'jan',
    'feb',
    'mar',
    'apr',
    'may',
    'jun',
    'jul',
    'aug',
    'sep',
    'oct',
    'nov',
    'dec',
])


WEEKDAYS = _enum([
    'sun',
    'mon',
    'tue',
    'wed',
    'thu',
    'fri',
    'sat',
    'sun',
])


class Range(dc.Pure):
    min: int = dc.field(check=int.__instancecheck__)
    max: int = dc.field(check=int.__instancecheck__)

    def __post_init__(self) -> None:
        check.arg(self.min <= self.max)

    def __str__(self) -> str:
        return f'[{self.min}, {self.max}]' if self.min != self.max else str(self.min)

    def __contains__(self, o: ta.Union['Range', int]) -> bool:
        if isinstance(o, Range):
            return self.min <= o.min and o.max <= self.max
        elif isinstance(o, int):
            return self.min <= o <= self.max
        else:
            raise TypeError(o)


class Field(dc.Pure):
    name: str
    idx: int
    rng: Range
    enum: ta.Optional[Enum] = None


MINUTE = Field('minute', 0, Range(0, 59))
HOUR = Field('hour', 1, Range(0, 23))
DAY = Field('day', 2, Range(1, 31))
MONTH = Field('month', 3, Range(1, 12), MONTHS)
WEEKDAY = Field('weekday', 4, Range(0, 6), WEEKDAYS)


FIELDS = [
    MINUTE,
    HOUR,
    DAY,
    MONTH,
    WEEKDAY,
]


class Item(dc.Pure):
    rngs: ta.Sequence[Range] = dc.field(coerce=seq, check=lambda l: l and all(isinstance(o, Range) for o in l))

    def __str__(self) -> str:
        return f"{','.join(self.rngs)}" if len(self.rngs) > 1 else str(check.single(self.rngs))

    def __iter__(self) -> ta.Iterator:
        return iter(self.rngs)


class Spec(dc.Pure):
    minute: ta.Optional[Item] = dc.field(None, kwonly=True)
    hour: ta.Optional[Item] = dc.field(None, kwonly=True)
    day: ta.Optional[Item] = dc.field(None, kwonly=True)
    month: ta.Optional[Item] = dc.field(None, kwonly=True)
    weekday: ta.Optional[Item] = dc.field(None, kwonly=True)

    def __str__(self):
        return ' '.join(str(i) if i is not None else '*' for f in FIELDS for i in [getattr(self, f.name)])

    @classmethod
    def parse(cls, s: str) -> 'Spec':
        parts = s.strip().split()
        check.arg(len(parts) == 5)
        kw = {}

        for p, f in zip(parts, FIELDS):
            check.not_empty(p)
            if p == '*':
                continue

            rs = []
            for sp in p.split(','):
                if '-' in sp:
                    bs = _, _ = sp.split('-')
                else:
                    bs = [sp, sp]

                if f.enum is not None:
                    bs = [f.enum.dct.get(b, b) for b in bs]

                l, r = map(int, bs)
                r = Range(l, r)
                check.arg(r in f.rng)
                rs.append(r)

            kw[f.name] = Item(rs)

        return cls(**kw)

    @classmethod
    def of(cls, obj: ta.Union['Spec', str]) -> 'Spec':
        if isinstance(obj, Spec):
            return obj
        elif isinstance(obj, str):
            return Spec.parse(obj)
        else:
            raise TypeError(obj)


SPECIALS = {k: Spec.parse(s) for k, s in {
    'hourly': '0 * * * *',
    'daily': '0 0 * * *',
    'weekly': '0 0 * * 0',
    'monthly': '0 0 1 * *',
    'yearly': '0 0 1 1 *',
    'annually': '0 0 1 1 *',
    'midnight': '0 0 * * *',
}.items()}
