##
# stdlib interface

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

    replace,
)

from .impl.api import (  # noqa
    dataclass as xdataclass,

    make_dataclass as xmake_dataclass,

    field as xfield,
)

from .impl.concerns.replace import (  # noqa
    replace as xreplace,
)

from .tools.as_ import (  # noqa
    asdict,
    astuple,
)


##
# globals hack

globals()['field'] = xfield

globals()['dataclass'] = xdataclass
globals()['make_dataclass'] = xmake_dataclass

globals()['replace'] = xreplace


##
# additional interface

from .impl.api import (  # noqa
    append_class_metadata,
    extra_class_params,
    init,
    metadata,
    validate,

    extra_field_params,
    set_field_metadata,
    update_extra_field_params,
    with_extra_field_params,
)

from .errors import (  # noqa
    FieldFnValidationError,
    FieldTypeValidationError,
    FieldValidationError,
    FnValidationError,
    TypeValidationError,
    ValidationError,
)

from .metaclass.bases import (  # noqa
    Box,
    Case,
    Data,
    Frozen,
)

from .metaclass.meta import (  # noqa
    DataMeta,
)

from .metaclass.specs import (  # noqa
    get_metaclass_spec,
)

from .reflection import (  # noqa
    reflect,
)

from .specs import (  # noqa
    CoerceFn,
    ValidateFn,
    ReprFn,

    InitFn,
    ClassValidateFn,

    DefaultFactory,

    FieldType,

    FieldSpec,

    ClassSpec,
)

from .tools.as_ import (  # noqa
    shallow_asdict,
    shallow_astuple,
)

from .tools.iter import (  # noqa
    fields_dict,

    iter_items,
    iter_keys,
    iter_values,
)

from .tools.modifiers import (  # noqa
    field_modifier,
    update_fields,
)

from .tools.only_ import (  # noqa
    only,
)

from .tools.replace import (  # noqa
    deep_replace,
)

from .tools.repr import (  # noqa
    opt_repr,
    truthy_repr,
)

from .tools.static import (  # noqa
    Static,
)


##
# lite imports

from ..lite.dataclasses import (  # noqa
    is_immediate_dataclass,

    dataclass_maybe_post_init as maybe_post_init,
)
