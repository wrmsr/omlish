# fmt: off
# ruff: noqa: I001
from omlish import marshal as _msh

_msh.register_global_module_import('._marshal', __package__)


##


# This is everything _marshal.py references - it must all be imported before the conditional import.

from . import (  # noqa
    code as _code,
    dynamic as _dynamic,
    images as _images,
    json as _json,
    quote as _quote,
    raw as _raw,
    section as _section,
    sequence as _sequence,
    tag as _tag,
    templates as _templates,
    text as _text,
)
