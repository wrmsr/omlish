from .base import Backend
from .std import STD_BACKEND
from .ujson import UJSON_BACKEND


DEFAULT_BACKED: Backend
if UJSON_BACKEND is not None:
    DEFAULT_BACKED = UJSON_BACKEND
else:
    DEFAULT_BACKED = STD_BACKEND
