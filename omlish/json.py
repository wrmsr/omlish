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
