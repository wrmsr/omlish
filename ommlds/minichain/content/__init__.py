# fmt: off
# ruff: noqa: I001
from omlish import lang as _lang


# This is everything _marshal.py references - it must all be imported before the conditional import.
from . import (  # noqa
    images as _images,
    materialize as _materialize,
    sequence as _sequence,
    text as _text,
    types as _types,
)


_lang.register_conditional_import('omlish.marshal', '._marshal', __package__)
