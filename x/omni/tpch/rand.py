import io

from .. import check
from .. import lang


class ByRow(lang.Interface):

    def row_finished(self) -> None: ...
    def advance_rows(self, row_count: int) -> None: ...


class Gen(ByRow, lang.Interface):

    def next(self) -> int: ...
    def rand(self, low_value: int, high_value: int) -> int: ...


class PyIntGen(Gen):

    _MULTIPLIER = 16807
    _MODULUS = 2147483647

    def __init__(self, seed: int, expected_usage_per_row: int) -> None:
        super().__init__()

        self._seed = check.isinstance(seed, int)
        self._expected_usage_per_row = check.isinstance(expected_usage_per_row, int)
        self._usage = 0

    def next(self) -> int:
        if self._usage >= self._expected_usage_per_row:
            raise ValueError
        self._seed = (self._seed * self._MULTIPLIER) % self._MODULUS
        self._usage += 1
        return self._seed

    def rand(self, low_value: int, high_value: int) -> int:
        self.next()
        int_range = high_value - low_value + 1
        double_range = float(int_range)
        value_in_range = int((1.0 * self._seed / self._MODULUS) * double_range)
        return low_value + value_in_range

    def _advance_seed(self, count: int) -> None:
        multiplier = self._MULTIPLIER
        while count > 0:
            if count % 2 != 0:
                self._seed = (multiplier * self._seed) % self._MODULUS
            count = count // 2
            multiplier = (multiplier * multiplier) % self._MODULUS

    def row_finished(self) -> None:
        self._advance_seed(self._expected_usage_per_row - self._usage)
        self._usage = 0

    def advance_rows(self, row_count: int) -> None:
        if self._usage:
            self.row_finished()
        self._advance_seed(self._expected_usage_per_row * row_count)


class PyLongGen(Gen):

    _MULTIPLIER = 6364136223846793005
    _INCREMENT = 1

    def __init__(self, seed: int, expected_usage_per_row: int) -> None:
        super().__init__()

        self._seed = check.isinstance(seed, int)
        self._expected_usage_per_row = check.isinstance(expected_usage_per_row, int)
        self._usage = 0

    def next(self) -> int:
        check.state(self._usage < self._expected_usage_per_row)
        self._seed = (self._seed * self._MULTIPLIER) + self._INCREMENT
        self._usage += 1
        return self._seed

    def rand(self, low_value: int, high_value: int) -> int:
        self.next()
        value_in_range = abs(self._seed) % (high_value - low_value + 1)
        return low_value + value_in_range

    _MULTIPLIER_32 = 16807
    _MODULUS_32 = 2147483647

    def _advance_seed(self, count: int) -> None:
        multiplier = self._MULTIPLIER_32
        while count > 0:
            if count % 2 != 0:
                self._seed = (multiplier * self._seed) % self._MODULUS_32
            count = count // 2
            multiplier = (multiplier * multiplier) % self._MODULUS_32

    def row_finished(self) -> None:
        self._advance_seed(self._expected_usage_per_row - self._usage)
        self._usage = 0

    def advance_rows(self, row_count: int) -> None:
        if self._usage != 0:
            self.row_finished()
        self._advance_seed(self._expected_usage_per_row * row_count)


_CY_ENABLED = False

try:
    if not _CY_ENABLED:
        raise ImportError

    from .._ext.cy.tpch import IntGen as CyIntGen
    from .._ext.cy.tpch import LongGen as CyLongGen

    IntGen = CyIntGen
    LongGen = CyLongGen

except ImportError:
    IntGen = PyIntGen
    LongGen = PyLongGen


class GenRandom(ByRow, lang.Abstract):

    def __init__(self, gen: Gen) -> None:
        super().__init__()

        self._gen = gen

    def row_finished(self) -> None:
        self._gen.row_finished()

    def advance_rows(self, row_count: int) -> None:
        self._gen.advance_rows(row_count)


class RandomInt(GenRandom):

    def __init__(self, seed: int, expected_usage_per_row: int) -> None:
        super().__init__(IntGen(seed, expected_usage_per_row))

    def rand(self, low_value: int, high_value: int) -> int:
        return self._gen.rand(low_value, high_value)


class RandomLong(GenRandom):

    def __init__(self, seed: int, expected_usage_per_row: int) -> None:
        super().__init__(LongGen(seed, expected_usage_per_row))

    def rand(self, low_value: int, high_value: int) -> int:
        return self._gen.rand(low_value, high_value)


class RandomAlphaNumeric(GenRandom):

    _ALPHA_NUMERIC = '0123456789abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ,'

    _LOW_LENGTH_MULTIPLIER = 0.4
    _HIGH_LENGTH_MULTIPLIER = 1.6

    _USAGE_PER_ROW = 9

    def __init__(
            self,
            seed: int,
            average_length: int,
            expected_row_count: int = 1,
    ) -> None:
        super().__init__(IntGen(seed, self._USAGE_PER_ROW * expected_row_count))

        self._min_length = int(average_length * self._LOW_LENGTH_MULTIPLIER)
        self._max_length = int(average_length * self._HIGH_LENGTH_MULTIPLIER)

    def next_value(self) -> str:
        sz = self._gen.rand(self._min_length, self._max_length)
        buf = io.StringIO()
        char_index = 0
        for i in range(sz):
            if i % 5 == 0:
                char_index = self._gen.rand(0, 0x7FFFFFFF)
            buf.write(self._ALPHA_NUMERIC[char_index & 0x3F])
            char_index = (char_index >> 6) & 0x7FFFFFFF
        return buf.getvalue()


class RandomBoundedInt(GenRandom):

    def __init__(
            self,
            seed: int,
            low_value: int,
            high_value: int,
            expected_row_count: int = 1,
    ) -> None:
        super().__init__(IntGen(seed, expected_row_count))

        self._low_value = low_value
        self._high_value = high_value

    def next_value(self) -> int:
        return self._gen.rand(self._low_value, self._high_value)


class RandomBoundedLong(GenRandom):

    def __init__(
            self,
            seed: int,
            use_64_bits: bool,
            low_value: int,
            high_value: int,
            expected_row_count: int = 1,
    ) -> None:
        gen_cls = LongGen if use_64_bits else IntGen
        super().__init__(gen_cls(seed, expected_row_count))

        self._low_value = low_value
        self._high_value = high_value

    def next_value(self) -> int:
        return self._gen.rand(self._low_value, self._high_value)


class RandomPhoneNumber(GenRandom):

    _NATIONS_MAX = 90  # limited by country codes in phone numbers

    def __init__(self, seed: int, expected_row_count: int = 1) -> None:
        super().__init__(IntGen(seed, 3 * expected_row_count))

    def next_value(self, nation_key: int) -> str:
        return '%02d-%03d-%03d-%04d' % (
            (10 + (nation_key % self._NATIONS_MAX)),
            self._gen.rand(100, 999),
            self._gen.rand(100, 999),
            self._gen.rand(1000, 9999),
        )
