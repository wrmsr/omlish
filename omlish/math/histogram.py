"""
TODO:
 - reservoir
 - dep tdigest?
 - struct-of-arrays - array.array('f', ...) - backed SamplingHistogram
 - https://docs.python.org/3/library/statistics.html
"""
import contextlib
import dataclasses as dc
import operator
import random
import time
import typing as ta

from .. import check


##


class SamplingHistogram:
    @dc.dataclass(frozen=True)
    class Entry:
        value: float
        timestamp: float

    @dc.dataclass(frozen=True)
    class Percentile:
        p: float
        value: float

    @dc.dataclass(frozen=True)
    class Stats:
        count: int
        min: float
        max: float
        last_percentiles: list['SamplingHistogram.Percentile']
        sample_percentiles: list['SamplingHistogram.Percentile']

    DEFAULT_SIZE = 1000
    DEFAULT_PERCENTILES = (0.5, 0.75, 0.9, 0.95, 0.99)

    def __init__(
            self,
            *,
            size: int = DEFAULT_SIZE,
            percentiles: ta.Iterable[float] | None = None,
    ) -> None:
        check.arg(size > 0)

        super().__init__()

        self._size = size
        self._percentiles = list(percentiles if percentiles is not None else self.DEFAULT_PERCENTILES)

        self._count = 0
        self._min = float('inf')
        self._max = float('-inf')

        self._percentile_pos_list = [self._calc_percentile_pos(p, self._size) for p in self._percentiles]

        self._ring: list[SamplingHistogram.Entry | None] = [None] * size
        self._ring_pos = 0

        self._sample: list[SamplingHistogram.Entry | None] = [None] * size
        self._sample_pos_queue = list(reversed(range(size)))

    def add(self, value: float) -> None:
        self._count += 1
        self._min = min(self._min, value)
        self._max = max(self._max, value)

        entry = self.Entry(value, time.time())

        self._ring[self._ring_pos] = entry
        next_ring_pos = self._ring_pos + 1
        self._ring_pos = 0 if next_ring_pos >= self._size else next_ring_pos

        sample_pos = None
        if self._sample_pos_queue:
            with contextlib.suppress(IndexError):
                sample_pos = self._sample_pos_queue.pop()
        if sample_pos is None:
            sample_pos = random.randrange(0, self._size)
        self._sample[sample_pos] = entry

    @staticmethod
    def _calc_percentile_pos(p: float, sz: int) -> int:
        return round((p * sz) - 1)

    def _calc_percentiles(self, entries: list[Entry | None]) -> list[Percentile]:
        entries = list(filter(None, entries))
        sz = len(entries)
        if not sz:
            return []
        elif sz == self._size:
            pos_list = self._percentile_pos_list
        else:
            pos_list = [self._calc_percentile_pos(p, sz) for p in self._percentiles]
        entries.sort(key=operator.attrgetter('value'))
        return [
            self.Percentile(p, check.not_none(entries[pos]).value)
            for p, pos in zip(self._percentiles, pos_list)
        ]

    def get(self) -> Stats:
        return self.Stats(
            count=self._count,
            min=self._min,
            max=self._max,
            last_percentiles=self._calc_percentiles(self._ring),
            sample_percentiles=self._calc_percentiles(self._sample),
        )

    def get_filtered(self, entry_filter: ta.Callable[[Entry], bool]) -> Stats:
        def filter_entries(l):
            return [e for e in list(l) if e is not None and entry_filter(e)]
        return self.Stats(
            count=self._count,
            min=self._min,
            max=self._max,
            last_percentiles=self._calc_percentiles(filter_entries(self._ring)),
            sample_percentiles=self._calc_percentiles(filter_entries(self._sample)),
        )

    def get_since(self, min_timestamp: float) -> Stats:
        return self.get_filtered(lambda e: e.timestamp >= min_timestamp)
