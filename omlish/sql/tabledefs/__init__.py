from .tabledefs import (  # noqa
    TableDef,
)


##


from ... import marshal as _msh

_msh.register_global_module_import('._marshal', __package__)
