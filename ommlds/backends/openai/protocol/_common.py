from omlish import lang
from omlish import marshal as msh


##


def _set_class_marshal_options(cls):
    msh.update_object_options(
        field_defaults=msh.FieldOptions(
            omit_if=lang.is_none,
        ),
    )(cls)

    return cls
