from omlish import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from .base import (  # noqa
    DateTime,
    MillisecondDateTime,
    Timestamp,

    Tag,
    TagList,

    ValueType,
    ListValueType,
    MapValueType,

    Enum,

    SHAPE_NAME,
    common_metadata,

    shape_metadata,
    ShapeInfo,
    Shape,

    MEMBER_NAME,
    SERIALIZATION_NAME,
    VALUE_TYPE,
    field_metadata,

    Operation,
)


##


from omlish import marshal as _msh  # noqa

_msh.register_global_module_import('._marshal', __package__)
