from omcore import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from omcore import marshal as _msh  # noqa


_msh.register_global_module_import('._marshal', __package__)
