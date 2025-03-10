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

    # asdict,
    # astuple,

    # replace,
)

from .impl.api import (  # noqa
    field as xfield,

    dataclass as xdataclass,
    make_dataclass as xmake_dataclass,

    extra_params,
)

from .impl.as_ import (  # noqa
    asdict,
    astuple,
)

from .impl.params import (  # noqa
    FieldExtras,
    get_field_extras,
)

from .impl.replace import (  # noqa
    replace,
)


##


globals()['field'] = xfield

globals()['dataclass'] = xdataclass
globals()['make_dataclass'] = xmake_dataclass


##


from .impl.exceptions import (  # noqa
    FieldValidationError,
    ValidationError,
)

from .impl.metaclass import (  # noqa
    DataMeta,
    Data,
    Frozen,
    Case,
    Box,
)

from .impl.metadata import (  # noqa
    Metadata,

    get_merged_metadata,

    UserMetadata,
    metadata,

    Validate,
    validate,

    Init,
    init,
)

from .impl.reflect import (  # noqa
    ClassInfo,
    reflect,
)

from .static import (  # noqa
    Static,
)

from .utils import (  # noqa
    opt_repr,
    truthy_repr,

    fields_dict,
    field_modifier,
    chain_metadata,
    update_class_metadata,
    update_field_metadata,
    update_field_extras,
    update_fields,
    update_fields_metadata,

    shallow_astuple,
    shallow_asdict,

    deep_replace,

    iter_items,
    iter_keys,
    iter_values,
)

##

from ..lite.dataclasses import (  # noqa
    is_immediate_dataclass,

    dataclass_maybe_post_init as maybe_post_init,
)
