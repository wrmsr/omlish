import functools
import json as _json


dump = _json.dump
dumps = _json.dumps

detect_encoding = _json.detect_encoding

load = _json.load
loads = _json.loads

##


PRETTY_INDENT = 2

PRETTY_KWARGS = dict(
    indent=PRETTY_INDENT,
)

dump_pretty = functools.partial(dump, **PRETTY_KWARGS)
dumps_pretty = functools.partial(dumps, **PRETTY_KWARGS)

##


COMPACT_SEPARATORS = (',', ':')

COMPACT_KWARGS = dict(
    indent=0,
    separators=COMPACT_SEPARATORS,
)

dump_compact = functools.partial(dump, **COMPACT_KWARGS)
dumps_compact = functools.partial(dumps, **COMPACT_KWARGS)


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
