from .tabledefs import (  # noqa
    TableDef,
)


##


from ... import lang as _lang

_lang.register_conditional_import('...marshal', '.marshal', __package__)
