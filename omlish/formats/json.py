"""
json
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

ujson
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

orjson
  dumps
    default
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

rapidjson
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
import functools
import json as _json
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import orjson as _orjson
    import ujson as _ujson
else:
    _orjson = lang.proxy_import('orjson')
    _ujson = lang.proxy_import('ujson')


##


dump = _json.dump
dumps = _json.dumps

detect_encoding = _json.detect_encoding

load = _json.load
loads = _json.loads


##


PRETTY_INDENT = 2

PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=PRETTY_INDENT,
)

dump_pretty: ta.Callable[..., bytes] = functools.partial(dump, **PRETTY_KWARGS)  # type: ignore
dumps_pretty: ta.Callable[..., str] = functools.partial(dumps, **PRETTY_KWARGS)


##


COMPACT_SEPARATORS = (',', ':')

COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=COMPACT_SEPARATORS,
)

dump_compact: ta.Callable[..., bytes] = functools.partial(dump, **COMPACT_KWARGS)  # type: ignore
dumps_compact: ta.Callable[..., str] = functools.partial(dumps, **COMPACT_KWARGS)


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
