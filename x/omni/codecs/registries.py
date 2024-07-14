import os
import typing as ta

from .. import check
from .. import registries
from .simple import composite
from .types import Codec


CodecT = ta.TypeVar('CodecT', bound=Codec)
CodecOrCodecType = ta.Union[Codec, ta.Type[CodecT]]


def _registry_validator(dct):
    for k, v in dct.items():
        check.not_empty(k)
        if not (isinstance(v, Codec) or (isinstance(v, type) and issubclass(v, Codec))):
            raise TypeError(v)


EXTENSION_REGISTRY: registries.Registry[str, ta.Type[CodecOrCodecType]] = registries.DictRegistry(validator=_registry_validator)  # noqa
MIME_TYPE_REGISTRY: registries.Registry[str, ta.Type[CodecOrCodecType]] = registries.DictRegistry(validator=_registry_validator)  # noqa


def for_file_name(file_name):
    return for_extension(os.path.basename(file_name).partition('.')[2])


def for_extension(ext):
    ext, _, rest = ext.partition('.')
    obj = EXTENSION_REGISTRY[ext]
    if isinstance(obj, type):
        if not issubclass(obj, Codec):
            raise TypeError(obj)
        obj = obj()
    else:
        if not isinstance(obj, Codec):
            raise TypeError(obj)
    if rest:
        return composite(obj, for_extension(rest))
    else:
        return obj
