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
    CheckError,
    FieldCheckError,
)

from .impl.metaclass import (  # noqa
    DataMeta,
    Data,
    Frozen,
    Box,
)

from .impl.metadata import (  # noqa
    get_merged_metadata,

    UserMetadata,
    metadata,

    Check,
    check,

    Init,
    init,
)

from .impl.reflect import (  # noqa
    ClassInfo,
    reflect,
)

from .utils import (  # noqa
    chain_metadata,
    deep_replace,
    field_modifier,
    maybe_post_init,
    opt_repr,
    update_field_extras,
    update_field_metadata,
)
