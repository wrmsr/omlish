"""
TODO:
 - reservoir
 - dep tdigest?
 - struct-of-arrays - array.array('f', ...) - backed SamplingHistogram
 - https://docs.python.org/3/library/statistics.html
"""
import bisect
import collections
import contextlib
import dataclasses as dc
import math
import operator
import random
import time
import typing as ta

from .. import cached
from .. import check


##


def get_quantile(sorted_data: ta.Sequence[float], q: float) -> float:
    q = float(q)
    check.arg(0.0 <= q <= 1.0)
    data, n = sorted_data, len(sorted_data)
    idx = q / 1.0 * (n - 1)
    idx_f, idx_c = math.floor(idx), math.ceil(idx)
    if idx_f == idx_c:
        return data[idx_f]
    return (data[idx_f] * (idx_c - idx)) + (data[idx_c] * (idx - idx_f))


##


class Stats(ta.Sequence[float]):
    """
    ~ https://github.com/mahmoud/boltons/blob/47e0c3bfcbd3291a1366f34069f23e43659717cd/boltons/statsutils.py
    """

    def __init__(
            self,
            data: ta.Sequence[float],
            *,
            default: float = 0.,
            eq: ta.Callable[[float, float], bool] = lambda a, b: a == b,
    ) -> None:
        super().__init__()

        self._kwargs: ta.Any = dict(
            default=default,
            eq=eq,
        )

        self._data = data
        self._default = default
        self._eq = eq

    @property
    def data(self) -> ta.Sequence[float]:
        return self._data

    @property
    def default(self) -> float:
        return self._default

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> ta.Iterator[float]:
        return iter(self.data)

    def __getitem__(self, index: ta.Any) -> float:  # type: ignore
        return self._data[index]

    @cached.property
    def sorted(self) -> ta.Sequence[float]:
        return sorted(self.data)

    @cached.property
    def mean(self) -> float:
        return sum(self.data, 0.0) / len(self.data)

    @cached.property
    def max(self) -> float:
        return max(self.data)

    @cached.property
    def min(self) -> float:
        return min(self.data)

    def get_quantile(self, q: float) -> float:
        if not self.data:
            return self.default
        return get_quantile(self.sorted, q)

    @cached.property
    def median(self) -> float:
        return self.get_quantile(0.5)

    def get_pow_diffs(self, power: float) -> list[float]:
        m = self.mean
        return [(v - m) ** power for v in self.data]

    @cached.property
    def variance(self) -> float:
        return Stats(self.get_pow_diffs(2)).mean

    @cached.property
    def std_dev(self) -> float:
        return self.variance ** 0.5

    @cached.property
    def median_abs_dev(self) -> float:
        x = self.median
        return Stats([abs(x - v) for v in self.sorted]).median

    @cached.property
    def rel_std_dev(self) -> float:
        abs_mean = abs(self.mean)
        if abs_mean:
            return self.std_dev / abs_mean
        else:
            return self.default

    @cached.property
    def skewness(self) -> float:
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self.get_pow_diffs(3)) / float((len(data) - 1) * (s_dev ** 3)))
        else:
            return self.default

    @cached.property
    def kurtosis(self) -> float:
        data, s_dev = self.data, self.std_dev
        if len(data) > 1 and s_dev > 0:
            return (sum(self.get_pow_diffs(4)) / float((len(data) - 1) * (s_dev ** 4)))
        else:
            return 0.0

    @cached.property
    def iqr(self) -> float:
        return self.get_quantile(0.75) - self.get_quantile(0.25)

    @cached.property
    def trimean(self) -> float:
        return (self.get_quantile(0.25) + (2 * self.get_quantile(0.5)) + self.get_quantile(0.75)) / 4.0

    def get_zscore(self, value: float) -> float:
        mean = self.mean
        if self._eq(self.std_dev, 0.0):
            if self._eq(value, mean):
                return 0
            if value > mean:
                return float('inf')
            if value < mean:
                return float('-inf')
        return (float(value) - mean) / self.std_dev

    def trim_relative(self, amount: float = 0.15) -> 'Stats':
        trim = float(amount)
        check.arg(0.0 <= trim < 0.5)
        size = len(self.data)
        size_diff = int(size * trim)
        if self._eq(size_diff, 0.0):
            return self
        return Stats(self.sorted[size_diff:-size_diff], **self._kwargs)

    def get_bin_bounds(
            self,
            count: int | None = None,
            with_max: bool = False,
    ) -> list[float]:
        if not self.data:
            return [0.0]

        data = self.data
        len_data, min_data, max_data = len(data), min(data), max(data)

        if len_data < 4:
            if not count:
                count = len_data
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        elif count is None:
            # freedman algorithm for fixed-width bin selection
            q25, q75 = self.get_quantile(0.25), self.get_quantile(0.75)
            dx = 2 * (q75 - q25) / (len_data ** (1 / 3.0))
            bin_count = max(1, math.ceil((max_data - min_data) / dx))
            bins = [min_data + (dx * i) for i in range(bin_count + 1)]
            bins = [b for b in bins if b < max_data]

        else:
            dx = (max_data - min_data) / float(count)
            bins = [min_data + (dx * i) for i in range(count)]

        if with_max:
            bins.append(float(max_data))

        return bins

    def get_histogram_counts(
            self,
            bins: list[float] | int | None = None,
            *,
            bin_digits: int = 1,
    ) -> list[tuple[float, int]]:
        bin_digits = int(bin_digits)
        if not bins:
            bins = self.get_bin_bounds()
        elif isinstance(bins, int):
            bins = self.get_bin_bounds(bins)
        else:
            bins = [float(x) for x in bins]
            if self.min < bins[0]:
                bins = [self.min, *bins]

        round_factor = 10.0 ** bin_digits
        bins = [math.floor(b * round_factor) / round_factor for b in bins]
        bins = sorted(set(bins))

        idxs = [bisect.bisect(bins, d) - 1 for d in self.data]
        count_map = collections.Counter(idxs)
        bin_counts = [(b, count_map.get(i, 0)) for i, b in enumerate(bins)]
        return bin_counts


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
