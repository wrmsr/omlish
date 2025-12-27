# fmt: off
# ruff: noqa: I001
from omlish import marshal as _msh

_msh.register_global_module_import('._marshal', __package__)


##


# This is everything _marshal.py references - it must all be imported before the conditional import.

from . import (  # noqa
    images as _images,
    sequence as _sequence,
    tag as _tag,
    text as _text,
    types as _types,
)

from .materialization import (  # noqa
    types as _materialize_types,
)
