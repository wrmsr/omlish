from omlish import lang
from omlish import marshal as msh


##


def _set_class_marshal_options(cls):
    msh.update_object_metadata(
        cls,
        field_defaults=msh.FieldMetadata(
            options=msh.FieldOptions(
                omit_if=lang.is_none,
            ),
        ),
    )

    return cls
