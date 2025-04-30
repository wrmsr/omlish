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
)

from .api import (  # noqa
    dataclass as xdataclass,

    make_dataclass as xmake_dataclass,

    field as xfield,
)

from .tools.as_ import (  # noqa
    asdict,
    astuple,
)

from .concerns.replace import (  # noqa
    replace,
)


##
# globals hack

globals()['field'] = xfield

globals()['dataclass'] = xdataclass
globals()['make_dataclass'] = xmake_dataclass


##
# additional interface

from .api import (  # noqa
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
