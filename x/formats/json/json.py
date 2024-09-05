"""
dump
  std
    skipkeys=False
    ensure_ascii=True
    check_circular=True
    allow_nan=True
    cls=None
    indent=None
    separators=None
    default=None
    sort_keys=False
  ujson
    ensure_ascii
    encode_html_chars
    escape_forward_slashes
    sort_keys
    indent
    allow_nan
    reject_bytes
    default
    separators
  orjson
    OPT_INDENT_2
    OPT_NAIVE_UTC
    OPT_NON_STR_KEYS
    OPT_OMIT_MICROSECONDS
    OPT_PASSTHROUGH_DATACLASS
    OPT_PASSTHROUGH_DATETIME
    OPT_PASSTHROUGH_SUBCLASS
    OPT_SERIALIZE_DATACLASS
    OPT_SERIALIZE_NUMPY
    OPT_SERIALIZE_UUID
    OPT_SORT_KEYS
    OPT_STRICT_INTEGER
    OPT_UTC_Z
  rapidjson
    skipkeys=False,
    ensure_ascii=True,
    write_mode=WM_COMPACT,
    write_mode|WM_COMPACT
    write_mode|WM_PRETTY
    write_mode|WM_SINGLE_LINE_ARRAY
    indent=4,
    default=None,
    sort_keys=False,
    number_mode=None,
    number_mode|NM_NONE
    number_mode|NM_DECIMAL
    number_mode|NM_NAN
    number_mode|NM_NATIVE
    datetime_mode=None,
    datetime_mode|DM_NONE
    datetime_mode|DM_ISO8601
    datetime_mode|DM_UNIX_TIME
    datetime_mode|DM_ONLY_SECONDS
    datetime_mode|DM_IGNORE_TZ
    datetime_mode|DM_NAIVE_IS_UTC
    datetime_mode|DM_SHIFT_TO_UTC
    uuid_mode=None,
    uuid_mode|UM_NONE
    uuid_mode|UM_CANONICAL
    uuid_mode|UM_HEX
    bytes_mode=BM_UTF8,
    bytes_mode|BM_NONE
    bytes_mode|BM_UTF8
    iterable_mode=IM_ANY_ITERABLE,
    iterable_mode|IM_ANY_ITERABLE
    iterable_mode|IM_ONLY_LISTS
    mapping_mode=MM_ANY_MAPPING,
    mapping_mode|MM_ANY_MAPPING
    mapping_mode|MM_ONLY_DICTS
    mapping_mode|MM_COERCE_KEYS_TO_STRINGS
    mapping_mode|MM_SKIP_NON_STRING_KEYS
    mapping_mode|MM_SORT_KEYS
    chunk_size
    allow_nan=True

load
  std
    cls=None
    object_hook=None
    parse_float=None
    parse_int=None
    parse_constant=None
    object_pairs_hook=None
  rapidjson
    object_hook=None,
    number_mode=None,
    datetime_mode=None,
    uuid_mode=None,
    parse_mode=None,
    parse_mode|PM_NONE
    parse_mode|PM_COMMENTS
    parse_mode|PM_TRAILING_COMMAS
    chunk_size=65536,
    allow_nan=True
"""


class Backend:
    pass


class JsonBackend(Backend):
    """
    dump
      skipkeys=False
      ensure_ascii=True
      check_circular=True
      allow_nan=True
      cls=None
      indent=None
      separators=None
      default=None
      sort_keys=False
    dumps
      ^
    load
      cls=None
      object_hook=None
      parse_float=None
      parse_int=None
      parse_constant=None
      object_pairs_hook=None
    loads
      ^
    """


class UjsonBackend(Backend):
    """
    dump
      ensure_ascii
      encode_html_chars
      escape_forward_slashes
      sort_keys
      indent
      allow_nan
      reject_bytes
      default
      separators
    dumps
      ^
    load
    loads
    """


class OrjsonBackend(Backend):
    """
    dumps
      default: Optional[Callable[[Any], Any]]
      option
        OPT_INDENT_2
        OPT_NAIVE_UTC
        OPT_NON_STR_KEYS
        OPT_OMIT_MICROSECONDS
        OPT_PASSTHROUGH_DATACLASS
        OPT_PASSTHROUGH_DATETIME
        OPT_PASSTHROUGH_SUBCLASS
        OPT_SERIALIZE_DATACLASS
        OPT_SERIALIZE_NUMPY
        OPT_SERIALIZE_UUID
        OPT_SORT_KEYS
        OPT_STRICT_INTEGER
        OPT_UTC_Z
    loads
    """


class RapidjsonBackend(Backend):
    """
    dump
      skipkeys=False,
      ensure_ascii=True,
      write_mode=WM_COMPACT,
        WM_COMPACT
        WM_PRETTY
        WM_SINGLE_LINE_ARRAY
      indent=4,
      default=None,
      sort_keys=False,
      number_mode=None,
        NM_NONE
        NM_DECIMAL
        NM_NAN
        NM_NATIVE
      datetime_mode=None,
        DM_NONE
        DM_ISO8601
        DM_UNIX_TIME
        DM_ONLY_SECONDS
        DM_IGNORE_TZ
        DM_NAIVE_IS_UTC
        DM_SHIFT_TO_UTC
      uuid_mode=None,
        UM_NONE
        UM_CANONICAL
        UM_HEX
      bytes_mode=BM_UTF8,
        BM_NONE
        BM_UTF8
      iterable_mode=IM_ANY_ITERABLE,
        IM_ANY_ITERABLE
        IM_ONLY_LISTS
      mapping_mode=MM_ANY_MAPPING,
        MM_ANY_MAPPING
        MM_ONLY_DICTS
        MM_COERCE_KEYS_TO_STRINGS
        MM_SKIP_NON_STRING_KEYS
        MM_SORT_KEYS
      chunk_size
      allow_nan=True
    dumps
      ^
      -chunk_size
    load
      object_hook=None,
      number_mode=None,
        ^
      datetime_mode=None,
        ^
      uuid_mode=None,
        ^
      parse_mode=None,
        PM_NONE
        PM_COMMENTS
        PM_TRAILING_COMMAS
      chunk_size=65536,
      allow_nan=True
    loads
      ^
      -chunk_size
    """


##


# import functools
# import typing as ta
#
# from . import cached
# from . import dataclasses as dc
#
#
# F = ta.TypeVar('F')
# T = ta.TypeVar('T')
# StrMap = ta.Mapping[str, ta.Any]
#
#
# ENCODING = 'utf-8'
# PRETTY_INDENT = 2
# COMPACT_SEPARATORS = (',', ':')
#
#
# Dumps = ta.Callable[[ta.Any], str]
# Dumpb = ta.Callable[[ta.Any], bytes]
# Loads = ta.Callable[[ta.Union[str, bytes, bytearray]], ta.Any]
#
#
# @dc.dataclass(frozen=True)
# class _Provider:
#     pretty_kwargs: StrMap = dc.field(default_factory=dict)
#     compact_kwargs: StrMap = dc.field(default_factory=dict)
#
#
# class Provider:
#
#     def __init__(self, json: ta.Any) -> None:
#         super().__init__()
#         self._json = json
#
#     @property
#     def json(self) -> ta.Any:
#         return self._json
#
#     @cached.property
#     def dumps(self) -> Dumps:
#         return self.json.dumps
#
#     @cached.property
#     def dumpb(self) -> Dumpb:
#         def dumpb(*args, **kwargs):
#             return fn(*args, **kwargs).encode(ENCODING)
#         fn = self.json.dumps
#         return functools.wraps(fn)(dumpb)
#
#     @cached.property
#     def loads(self) -> Loads:
#         return self.json.loads
#
#     @cached.property
#     def pretty_kwargs(self) -> StrMap:
#         return {}
#
#     @cached.property
#     def compact_kwargs(self) -> StrMap:
#         return {}
#
#
# class OrjsonProvider(Provider):
#
#     def __init__(self) -> None:
#         import orjson
#         super().__init__(orjson)
#
#     @cached.property
#     def pretty_kwargs(self) -> StrMap:
#         return {
#             'option': self.json.OPT_INDENT_2,
#         }
#
#     @cached.property
#     def dumps(self) -> Dumps:
#         def dumps(*args, **kwargs):
#             return fn(*args, **kwargs).decode(ENCODING)
#         fn = self.json.dumps
#         return functools.wraps(fn)(dumps)
#
#     @cached.property
#     def dumpb(self) -> Dumpb:
#         return self.json.dumps
#
#
# class UjsonProvider(Provider):
#
#     def __init__(self) -> None:
#         import ujson
#         super().__init__(ujson)
#
#     @cached.property
#     def pretty_kwargs(self) -> StrMap:
#         return {
#             'indent': PRETTY_INDENT,
#         }
#
#     @cached.property
#     def loads(self) -> Loads:
#         def loads(arg, *args, **kwargs):
#             if isinstance(arg, (bytes, bytearray)):
#                 arg = arg.decode(ENCODING)
#             return fn(arg, *args, **kwargs)
#         fn = self.json.loads
#         return functools.wraps(fn)(loads)
#
#
# class BuiltinProvider(Provider):
#
#     def __init__(self) -> None:
#         import json
#         super().__init__(json)
#
#     @cached.property
#     def pretty_kwargs(self) -> StrMap:
#         return {
#             'indent': PRETTY_INDENT,
#         }
#
#     @cached.property
#     def compact_kwargs(self) -> StrMap:
#         return {
#             'indent': 0,
#             'separators': COMPACT_SEPARATORS,
#         }
#
#
# def _select_provider(typs: ta.Iterable[ta.Callable[[], Provider]]) -> Provider:
#     for typ in typs:
#         try:
#             return typ()
#         except ImportError:
#             pass
#     raise TypeError('No suitable json providers')
#
#
# PROVIDER: Provider = _select_provider([
#     OrjsonProvider,
#     UjsonProvider,
#     BuiltinProvider,
# ])
#
#
# dumps: Dumps = PROVIDER.dumps
# dumpb: Dumpb = PROVIDER.dumpb
# loads: Loads = PROVIDER.loads
#
# dumps_compact: Dumps = functools.partial(dumps, **PROVIDER.compact_kwargs)
# dumpb_compact: Dumpb = functools.partial(dumpb, **PROVIDER.compact_kwargs)
#
# dumps_pretty: Dumps = functools.partial(dumps, **PROVIDER.pretty_kwargs)
# dumpb_pretty: Dumpb = functools.partial(dumpb, **PROVIDER.pretty_kwargs)

import dataclasses as dc
import enum

import rapidjson as rj


@dc.dataclass(frozen=True, kw_only=True)
class WriteMode(enum.Enum):
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
    canonical: bool = False
    hex: bool = False

    def __int__(self) -> int:
        return (
            (rj.UM_NONE if self.none else 0) |
            (rj.UM_CANONICAL if self.canonical else 0) |
            (rj.UM_HEX if self.hex else 0)
        )

@dc.dataclass(frozen=True, kw_only=True)
class BytesMode:
    none: bool = False
    utf8: bool = False

    def __int__(self) -> int:
        return (
            (rj.BM_NONE if self.none else 0) |
            (rj.BM_UTF8 if self.utf8 else 0)
        )

@dc.dataclass(frozen=True, kw_only=True)
class IterableMode:
    any_iterable: bool = False
    only_lists: bool = False

    def __int__(self) -> int:
        return (
            (rj.IM_ANY_ITERABLE if self.any_iterable else 0) |
            (rj.IM_ONLY_LISTS if self.only_lists else 0)
        )

@dc.dataclass(frozen=True, kw_only=True)
class MappingMode:
    any_mapping: bool = False
    only_dicts: bool = False
    coerce_keys_to_strings: bool = False
    skip_non_string_keys: bool = False
    sort_keys: bool = False

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
    comments: bool = False
    trailing_commas: bool = False

    def __int__(self) -> int:
        return (
            (rj.PM_NONE if self.none else 0) |
            (rj.PM_COMMENTS if self.comments else 0) |
            (rj.PM_TRAILING_COMMAS if self.trailing_commas else 0)
        )
