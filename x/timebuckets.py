import datetime
import typing as ta


def round_to_minute(dt: datetime.datetime) -> datetime.datetime:
    return dt.replace(second=0, microsecond=0)


class DateBucketCounter:
    def __init__(self, base: datetime.datetime | None = None) -> None:
        super().__init__()
        self._base: datetime.datetime = \
            round_to_minute(base) if base is not None else (datetime.datetime.min + datetime.timedelta(days=1))
        self._minutes: list[int] = [0] * 60
        self._hours: list[int] = [0] * 23
        self._days: dict[datetime.date, int] = {}
    
    def _add_to_day(self, day: datetime.date, n: int) -> None:
        self._days[day] = self._days.get(day, 0) + n
    
    def __iter__(self) -> ta.Iterator[tuple[datetime.datetime, datetime.timedelta, int]]:
         for i, n in enumerate(self._minutes):
             yield (self._base - (td := datetime.timedelta(minutes=i)), td, n)
         for i, n in enumerate(self._hours):
             yield (self._base - (td := datetime.timedelta(hours=i + 1)), td, n)
         for d, n in sorted(self._days.items()):
             yield (d, d + datetime.timedelta(days=1), n)

    def add(self, at: datetime.datetime | None = None, n: int = 1) -> None:
        if at is None:
            at = datetime.datetime.now()
        at = round_to_minute(at)
        if at < self._base:
            raise NotImplementedError
        td = at - self._base
        ts = int(td.total_seconds())
        if ts < 3600:
            nm = ts // 60
            if nm < 1:
                self._minutes[0] += n
                return
            sm = sum(self._minutes[-nm:])
            self._add_to_day((self._base - datetime.timedelta(days=1)).date(), self._hours[-1])
            self._hours = [sm] + self._hours[:-1]
            self._minutes = ([0] * nm) + self._minutes[:-nm]
            self._minutes[0] = n
            self._base = at
            return
        # for i, n in enumerate(self._minutes):
        #     cur = self._base - datetime.timedelta(minutes=n)
        #     print(cur)
        raise NotImplementedError

    def num_since(self, since: datetime.datetime | None = None) -> int:
        raise NotImplementedError


def _main() -> None:
    st = datetime.datetime.now() - datetime.timedelta(days=30)
    tb = DateBucketCounter(st)

    for tup in tb:
        print(tup)

    tb.add(st)
    tb.add(st + datetime.timedelta(minutes=1))
    tb.add(st + datetime.timedelta(minutes=2))
    tb.add(st + datetime.timedelta(hours=1))
    tb.add(st + datetime.timedelta(hours=1, minutes=1))
    tb.add(st + datetime.timedelta(hours=1, minutes=2))
    tb.add(st + datetime.timedelta(hours=2))
    tb.add(st + datetime.timedelta(hours=3))

    assert tb.num_since() == 4


if __name__ == '__main__':
    _main()
