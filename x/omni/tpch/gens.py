import typing as ta

from .. import check
from .ents import Customer
from .ents import Region
from .rand import RandomAlphaNumeric
from .rand import RandomBoundedInt
from .rand import RandomPhoneNumber
from .text import RandomString
from .text import RandomText
from .text import TextDists
from .text import TextPool


def calculate_row_count(scale_base: int, scale_factor: float, part: int, part_count: int) -> int:
    total_row_count = int(scale_base * scale_factor)
    row_count = total_row_count // part_count
    if part == part_count:
        # for the last part, add the remainder rows
        row_count += total_row_count % part_count
    return row_count


def calculate_start_index(scale_base: int, scale_factor: float, part: int, part_count: int) -> int:
    total_row_count = int(scale_base * scale_factor)
    rows_per_part = total_row_count // part_count
    return rows_per_part * (part - 1)


GENERATED_DATE_EPOCH_OFFSET = 83966  # The value of 1970-01-01 in the date generator system
MIN_GENERATE_DATE = 92001
CURRENT_DATE = 95168
TOTAL_DATE_RANGE = 2557

MONTH_YEAR_DAY_START = [
    0,
    31,
    59,
    90,
    120,
    151,
    181,
    212,
    243,
    273,
    304,
    334,
    365,
]


def _is_leap_year(year: int) -> bool:
    return year % 4 == 0 and year % 100 != 0


def _leap_year_adjustment(year: int, month: int) -> int:
    return 1 if _is_leap_year(year) and (month) >= 2 else 0


def _julian(date: int) -> int:
    offset = date - MIN_GENERATE_DATE
    result = MIN_GENERATE_DATE
    while True:
        year = result // 1000
        year_end = year * 1000 + 365 + (1 if _is_leap_year(year) else 0)
        if result + offset <= year_end:
            break
        offset -= year_end - result + 1
        result += 1000
    return result + offset


def _make_date(index: int) -> str:
    y = _julian(index + MIN_GENERATE_DATE - 1) // 1000
    d = _julian(index + MIN_GENERATE_DATE - 1) % 1000
    m = 0
    while d > MONTH_YEAR_DAY_START[m] + _leap_year_adjustment(y, m):
        m += 1
    dy = d - MONTH_YEAR_DAY_START[m - 1] - (1 if _is_leap_year(y) and m > 2 else 0)
    return '19%02d-%02d-%02d' % (y, m, dy)


DATE_STRING_INDEX = [_make_date(i + 1) for i in range(TOTAL_DATE_RANGE)]


def to_epoch_date(generated_date: int) -> int:
    return generated_date - GENERATED_DATE_EPOCH_OFFSET


def format_date(epoch_date: int) -> str:
    return DATE_STRING_INDEX[epoch_date - (MIN_GENERATE_DATE - GENERATED_DATE_EPOCH_OFFSET)]


def is_in_past(date: int) -> bool:
    return _julian(date) <= CURRENT_DATE


class RegionGenerator(ta.Iterable[Region]):

    _COMMENT_AVERAGE_LENGTH = 72

    def __init__(
            self,
            text_dists: TextDists = None,
            text_pool: TextPool = None,
    ) -> None:
        super().__init__()

        self._text_dists = check.isinstance(text_dists, TextDists) if text_dists is not None else TextDists.DEFAULT
        self._text_pool = check.isinstance(text_pool, TextPool) if text_pool is not None else TextPool.DEFAULT

    def __iter__(self) -> ta.Iterator[Customer]:
        # market_segment_random = RandomString(1140279430, self._text_dists.market_segments)
        comment_random = RandomText(1500869201, self._text_pool, self._COMMENT_AVERAGE_LENGTH)

        for index in range(self._text_dists.regions.size):
            region = Region(
                index,
                index,
                self._text_dists.regions.values[index],
                comment_random.next_value(),
            )

            yield region

            comment_random.row_finished()


class CustomerGenerator(ta.Iterable[Customer]):

    _SCALE_BASE = 150_000
    _ACCOUNT_BALANCE_MIN = -99999
    _ACCOUNT_BALANCE_MAX = 999999
    _ADDRESS_AVERAGE_LENGTH = 25
    _COMMENT_AVERAGE_LENGTH = 73

    def __init__(
            self,
            scale_factor: float,
            part: int,
            part_count: int,
            text_dists: TextDists = None,
            text_pool: TextPool = None,
    ) -> None:
        super().__init__()

        check.arg(scale_factor > 0)
        check.arg(part >= 1)
        check.arg(part <= part_count)

        self._scale_factor = scale_factor
        self._part = part
        self._part_count = part_count

        self._text_dists = check.isinstance(text_dists, TextDists) if text_dists is not None else TextDists.DEFAULT
        self._text_pool = check.isinstance(text_pool, TextPool) if text_pool is not None else TextPool.DEFAULT

    def __iter__(self) -> ta.Iterator[Customer]:
        start_index = calculate_start_index(self._SCALE_BASE, self._scale_factor, self._part, self._part_count)
        row_count = calculate_row_count(self._SCALE_BASE, self._scale_factor, self._part, self._part_count)

        address_random = RandomAlphaNumeric(881155353, self._ADDRESS_AVERAGE_LENGTH)
        nation_key_random = RandomBoundedInt(1489529863, 0, self._text_dists.nations.size - 1)
        phone_random = RandomPhoneNumber(1521138112)
        account_balance_random = RandomBoundedInt(298370230, self._ACCOUNT_BALANCE_MIN, self._ACCOUNT_BALANCE_MAX)
        market_segment_random = RandomString(1140279430, self._text_dists.market_segments)
        comment_random = RandomText(1335826707, self._text_pool, self._COMMENT_AVERAGE_LENGTH)

        for index in range(row_count):
            customer_key = start_index + index + 1
            nation_key = nation_key_random.next_value()

            customer = Customer(
                customer_key,
                customer_key,
                'Customer#%09d' % (customer_key,),
                address_random.next_value(),
                nation_key,
                phone_random.next_value(nation_key),
                account_balance_random.next_value(),
                market_segment_random.next_value(),
                comment_random.next_value(),
            )

            yield customer

            address_random.row_finished()
            nation_key_random.row_finished()
            phone_random.row_finished()
            account_balance_random.row_finished()
            market_segment_random.row_finished()
            comment_random.row_finished()
