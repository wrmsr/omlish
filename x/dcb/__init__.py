from dataclasses import (  # noqa
    FrozenInstanceError,

    MISSING,
    KW_ONLY,

    InitVar,
    Field,

    field,

    dataclass,
    make_dataclass,

    fields,

    is_dataclass,
)

from .api.api import (  # noqa
    field as xfield,

    dataclass as xdataclass,
    make_dataclass as xmake_dataclass,
)

from .api.classes.metadata import (
    extra_class_params,
    init,
    validate,
)

from .api.fields.metadata import (
    extra_field_params,
)

from .tools.as_ import (  # noqa
    asdict,
    astuple,
)

from .concerns.replace import (  # noqa
    replace,
)


##


globals()['field'] = xfield

globals()['dataclass'] = xdataclass
globals()['make_dataclass'] = xmake_dataclass


##


from .errors import (  # noqa
    FieldFnValidationError,
    FieldTypeValidationError,
    FieldValidationError,
    FnValidationError,
    TypeValidationError,
    ValidationError,
)
