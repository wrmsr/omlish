import bisect
import collections
import math
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
