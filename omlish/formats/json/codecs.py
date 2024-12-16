from ..codecs import make_object_lazy_loaded_codec
from ..codecs import make_str_object_codec
from .json import dumps
from .json import dumps_compact
from .json import dumps_pretty
from .json import loads


##


JSON_CODEC = make_str_object_codec('json', dumps, loads)

# @omlish-manifest
_JSON_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'JSON_CODEC', JSON_CODEC)

#

JSON_COMPACT_CODEC = make_str_object_codec('json-compact', dumps_compact, loads)

# @omlish-manifest
_JSON_COMPACT_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'JSON_COMPACT_CODEC', JSON_COMPACT_CODEC)

#

JSON_PRETTY_CODEC = make_str_object_codec('json-pretty', dumps_pretty, loads)

# @omlish-manifest
_JSON_PRETTY_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'JSON_PRETTY_CODEC', JSON_PRETTY_CODEC)
