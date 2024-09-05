"""

"""
import dataclasses as dc

import rapidjson as rj


@dc.dataclass(frozen=True, kw_only=True)
class WriteMode:
    compact: bool = False
    pretty: bool = False  # use PrettyWriter
    single_line_array: bool = False  # format arrays on a single line

    def __int__(self) -> int:
        return (
            (rj.WM_COMPACT if self.compact else 0) |
            (rj.WM_PRETTY if self.pretty else 0) |
            (rj.WM_SINGLE_LINE_ARRAY if self.single_line_array else 0)
        )


@dc.dataclass(frozen=True, kw_only=True)
class NumberMode:
    none: bool = False
    decimal: bool = False  # serialize Decimal instances, deserialize floats as Decimal
    nan: bool = False  # allow "not-a-number" values
    native: bool = False  # use faster native C library number handling

    def __int__(self) -> int:
        return (
            (rj.NM_NONE if self.none else 0) |
            (rj.NM_DECIMAL if self.decimal else 0) |
            (rj.NM_NAN if self.nan else 0) |
            (rj.NM_NATIVE if self.native else 0)
        )


@dc.dataclass(frozen=True, kw_only=True)
class DatetimeMode:
    none: bool = False

    # formats
    iso8601: bool = False  # bidirectional ISO8601 for datetimes, dates and times
    unix_time: bool = False  # serialization only, "Unix epoch"-based number of seconds

    # options
    only_seconds: bool = False  # truncate values to the whole second, ignoring micro seconds
    ignore_tz: bool = False  # ignore timezones
    naive_is_utc: bool = False  # assume naive datetime are in UTC timezone
    shift_to_utc: bool = False  # shift to/from UTC

    def __int__(self) -> int:
        return (
            (rj.DM_NONE if self.none else 0) |

            (rj.DM_ISO8601 if self.iso8601 else 0) |
            (rj.DM_UNIX_TIME if self.unix_time else 0) |

            (rj.DM_ONLY_SECONDS if self.only_seconds else 0) |
            (rj.DM_IGNORE_TZ if self.ignore_tz else 0) |
            (rj.DM_NAIVE_IS_UTC if self.naive_is_utc else 0) |
            (rj.DM_SHIFT_TO_UTC if self.shift_to_utc else 0)
        )


@dc.dataclass(frozen=True, kw_only=True)
class UuidMode:
    none: bool = False
    canonical: bool = False  # 4-dashed 32 hex chars: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    hex: bool = False  # canonical OR 32 hex chars in a row

    def __int__(self) -> int:
        return (
            (rj.UM_NONE if self.none else 0) |
            (rj.UM_CANONICAL if self.canonical else 0) |
            (rj.UM_HEX if self.hex else 0)
        )


@dc.dataclass(frozen=True, kw_only=True)
class BytesMode:
    none: bool = False
    utf8: bool = False  # try to convert to UTF-8

    def __int__(self) -> int:
        return (
            (rj.BM_NONE if self.none else 0) |
            (rj.BM_UTF8 if self.utf8 else 0)
        )


@dc.dataclass(frozen=True, kw_only=True)
class IterableMode:
    any_iterable: bool = False  # default, any iterable is dumped as JSON array
    only_lists: bool = False  # only list instances are dumped as JSON arrays

    def __int__(self) -> int:
        return (
            (rj.IM_ANY_ITERABLE if self.any_iterable else 0) |
            (rj.IM_ONLY_LISTS if self.only_lists else 0)
        )


@dc.dataclass(frozen=True, kw_only=True)
class MappingMode:
    any_mapping: bool = False  # default, any mapping is dumped as JSON object
    only_dicts: bool = False  # only dict instances are dumped as JSON objects
    coerce_keys_to_strings: bool = False  # convert keys to strings
    skip_non_string_keys: bool = False  # ignore non-string keys
    sort_keys: bool = False  # sort keys

    def __int__(self) -> int:
        return (
            (rj.MM_ANY_MAPPING if self.any_mapping else 0) |
            (rj.MM_ONLY_DICTS if self.only_dicts else 0) |
            (rj.MM_COERCE_KEYS_TO_STRINGS if self.coerce_keys_to_strings else 0) |
            (rj.MM_SKIP_NON_STRING_KEYS if self.skip_non_string_keys else 0) |
            (rj.MM_SORT_KEYS if self.sort_keys else 0)
        )


@dc.dataclass(frozen=True, kw_only=True)
class ParseMode:
    none: bool = False
    comments: bool = False  # allow one-line // ... and multi-line /* ... */ comments
    trailing_commas: bool = False  # allow trailing commas at the end of objects and arrays

    def __int__(self) -> int:
        return (
            (rj.PM_NONE if self.none else 0) |
            (rj.PM_COMMENTS if self.comments else 0) |
            (rj.PM_TRAILING_COMMAS if self.trailing_commas else 0)
        )
