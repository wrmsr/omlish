from .base import Backend
from .orjson import ORJSON_BACKEND
from .std import STD_BACKEND
from .ujson import UJSON_BACKEND


DEFAULT_BACKED: Backend
if ORJSON_BACKEND is not None:
    DEFAULT_BACKED = ORJSON_BACKEND
elif UJSON_BACKEND is not None:
    DEFAULT_BACKED = UJSON_BACKEND
else:
    DEFAULT_BACKED = STD_BACKEND
