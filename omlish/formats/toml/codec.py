import tomllib

from ..codecs import make_object_lazy_loaded_codec
from ..codecs import make_str_object_codec


##


def _dumps(obj):
    raise TypeError('Unsupported')


TOML_CODEC = make_str_object_codec('toml', _dumps, tomllib.loads)

# @omlish-manifest
_TOML_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'TOML_CODEC', TOML_CODEC)
