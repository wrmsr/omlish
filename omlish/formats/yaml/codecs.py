"""
TODO:
 - abstract backends like json
"""
from ..codecs import make_object_lazy_loaded_codec
from ..codecs import make_str_object_codec
from .pyyaml import dump
from .pyyaml import full_load
from .pyyaml import safe_load


##


YAML_CODEC = make_str_object_codec('yaml', dump, safe_load, aliases=['yml'])

# @omlish-manifest
_YAML_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'YAML_CODEC', YAML_CODEC)

#

YAML_UNSAFE_CODEC = make_str_object_codec('yaml-unsafe', dump, full_load)

# @omlish-manifest
_YAML_UNSAFE_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'YAML_UNSAFE_CODEC', YAML_UNSAFE_CODEC)
