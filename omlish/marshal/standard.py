from .any import ANY_MARSHALER_FACTORY
from .any import ANY_UNMARSHALER_FACTORY
from .base import MarshalerFactory
from .base import RecursiveMarshalerFactory
from .base import RecursiveUnmarshalerFactory
from .base import UnmarshalerFactory
from .base64 import BASE64_MARSHALER_FACTORY
from .base64 import BASE64_UNMARSHALER_FACTORY
from .dataclasses import DataclassMarshalerFactory
from .dataclasses import DataclassUnmarshalerFactory
from .datetimes import DATETIME_MARSHALER_FACTORY
from .datetimes import DATETIME_UNMARSHALER_FACTORY
from .enums import EnumMarshalerFactory
from .enums import EnumUnmarshalerFactory
from .factories import CompositeFactory
from .factories import TypeCacheFactory
from .iterables import IterableMarshalerFactory
from .iterables import IterableUnmarshalerFactory
from .mappings import MappingMarshalerFactory
from .mappings import MappingUnmarshalerFactory
from .optionals import OptionalMarshalerFactory
from .optionals import OptionalUnmarshalerFactory
from .primitives import PRIMITIVE_MARSHALER_FACTORY
from .primitives import PRIMITIVE_UNMARSHALER_FACTORY
from .uuids import UUID_MARSHALER_FACTORY
from .uuids import UUID_UNMARSHALER_FACTORY


##


STANDARD_MARSHALER_FACTORIES: list[MarshalerFactory] = [
    PRIMITIVE_MARSHALER_FACTORY,
    OptionalMarshalerFactory(),
    DataclassMarshalerFactory(),
    EnumMarshalerFactory(),
    UUID_MARSHALER_FACTORY,
    BASE64_MARSHALER_FACTORY,
    DATETIME_MARSHALER_FACTORY,
    MappingMarshalerFactory(),
    IterableMarshalerFactory(),
    ANY_MARSHALER_FACTORY,
]


def new_standard_marshaler_factory() -> MarshalerFactory:
    return TypeCacheFactory(  # noqa
        RecursiveMarshalerFactory(
            CompositeFactory(
                *STANDARD_MARSHALER_FACTORIES
            )
        )
    )


##


STANDARD_UNMARSHALER_FACTORIES: list[UnmarshalerFactory] = [
    PRIMITIVE_UNMARSHALER_FACTORY,
    OptionalUnmarshalerFactory(),
    DataclassUnmarshalerFactory(),
    EnumUnmarshalerFactory(),
    UUID_UNMARSHALER_FACTORY,
    BASE64_UNMARSHALER_FACTORY,
    DATETIME_UNMARSHALER_FACTORY,
    MappingUnmarshalerFactory(),
    IterableUnmarshalerFactory(),
    ANY_UNMARSHALER_FACTORY,
]


def new_standard_unmarshaler_factory() -> UnmarshalerFactory:
    return TypeCacheFactory(  # noqa
        RecursiveUnmarshalerFactory(
            CompositeFactory(
                *STANDARD_UNMARSHALER_FACTORIES
            )
        )
    )
