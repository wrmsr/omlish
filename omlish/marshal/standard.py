from .. import matchfns as mfs
from .any import ANY_MARSHALER_FACTORY
from .any import ANY_UNMARSHALER_FACTORY
from .base import MarshalerFactory
from .base import RecursiveMarshalerFactory
from .base import RecursiveUnmarshalerFactory
from .base import TypeCacheMarshalerFactory
from .base import TypeCacheUnmarshalerFactory
from .base import UnmarshalerFactory
from .base64 import BASE64_MARSHALER_FACTORY
from .base64 import BASE64_UNMARSHALER_FACTORY
from .dataclasses import DataclassMarshalerFactory
from .dataclasses import DataclassUnmarshalerFactory
from .datetimes import DATETIME_MARSHALER_FACTORY
from .datetimes import DATETIME_UNMARSHALER_FACTORY
from .enums import EnumMarshalerFactory
from .enums import EnumUnmarshalerFactory
from .iterables import IterableMarshalerFactory
from .iterables import IterableUnmarshalerFactory
from .mappings import MappingMarshalerFactory
from .mappings import MappingUnmarshalerFactory
from .maybes import MaybeMarshalerFactory
from .maybes import MaybeUnmarshalerFactory
from .newtypes import NewtypeMarshalerFactory
from .newtypes import NewtypeUnmarshalerFactory
from .numbers import NUMBERS_MARSHALER_FACTORY
from .numbers import NUMBERS_UNMARSHALER_FACTORY
from .optionals import OptionalMarshalerFactory
from .optionals import OptionalUnmarshalerFactory
from .primitives import PRIMITIVE_MARSHALER_FACTORY
from .primitives import PRIMITIVE_UNMARSHALER_FACTORY
from .unions import PrimitiveUnionMarshalerFactory
from .unions import PrimitiveUnionUnmarshalerFactory
from .uuids import UUID_MARSHALER_FACTORY
from .uuids import UUID_UNMARSHALER_FACTORY


##


STANDARD_MARSHALER_FACTORIES: list[MarshalerFactory] = [
    PRIMITIVE_MARSHALER_FACTORY,
    NewtypeMarshalerFactory(),
    OptionalMarshalerFactory(),
    PrimitiveUnionMarshalerFactory(),
    DataclassMarshalerFactory(),
    EnumMarshalerFactory(),
    NUMBERS_MARSHALER_FACTORY,
    UUID_MARSHALER_FACTORY,
    BASE64_MARSHALER_FACTORY,
    DATETIME_MARSHALER_FACTORY,
    MaybeMarshalerFactory(),
    MappingMarshalerFactory(),
    IterableMarshalerFactory(),
    ANY_MARSHALER_FACTORY,
]


def new_standard_marshaler_factory() -> MarshalerFactory:
    return TypeCacheMarshalerFactory(
        RecursiveMarshalerFactory(
            mfs.MultiMatchFn(
                list(STANDARD_MARSHALER_FACTORIES),
            ),
        ),
    )


##


STANDARD_UNMARSHALER_FACTORIES: list[UnmarshalerFactory] = [
    PRIMITIVE_UNMARSHALER_FACTORY,
    NewtypeUnmarshalerFactory(),
    OptionalUnmarshalerFactory(),
    PrimitiveUnionUnmarshalerFactory(),
    DataclassUnmarshalerFactory(),
    EnumUnmarshalerFactory(),
    NUMBERS_UNMARSHALER_FACTORY,
    UUID_UNMARSHALER_FACTORY,
    BASE64_UNMARSHALER_FACTORY,
    DATETIME_UNMARSHALER_FACTORY,
    MaybeUnmarshalerFactory(),
    MappingUnmarshalerFactory(),
    IterableUnmarshalerFactory(),
    ANY_UNMARSHALER_FACTORY,
]


def new_standard_unmarshaler_factory() -> UnmarshalerFactory:
    return TypeCacheUnmarshalerFactory(
        RecursiveUnmarshalerFactory(
            mfs.MultiMatchFn(
                list(STANDARD_UNMARSHALER_FACTORIES),
            ),
        ),
    )
