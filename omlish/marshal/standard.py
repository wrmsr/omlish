from .base import MarshalerFactory
from .base import MultiMarshalerFactory
from .base import MultiUnmarshalerFactory
from .base import RecursiveMarshalerFactory
from .base import RecursiveUnmarshalerFactory
from .base import TypeCacheMarshalerFactory
from .base import TypeCacheUnmarshalerFactory
from .base import UnmarshalerFactory
from .composite.iterables import IterableMarshalerFactory
from .composite.iterables import IterableUnmarshalerFactory
from .composite.literals import LiteralMarshalerFactory
from .composite.literals import LiteralUnmarshalerFactory
from .composite.mappings import MappingMarshalerFactory
from .composite.mappings import MappingUnmarshalerFactory
from .composite.maybes import MaybeMarshalerFactory
from .composite.maybes import MaybeUnmarshalerFactory
from .composite.newtypes import NewtypeMarshalerFactory
from .composite.newtypes import NewtypeUnmarshalerFactory
from .composite.optionals import OptionalMarshalerFactory
from .composite.optionals import OptionalUnmarshalerFactory
from .composite.special import SequenceNotStrMarshalerFactory
from .composite.special import SequenceNotStrUnmarshalerFactory
from .objects.dataclasses import DataclassMarshalerFactory
from .objects.dataclasses import DataclassUnmarshalerFactory
from .objects.namedtuples import NamedtupleMarshalerFactory
from .objects.namedtuples import NamedtupleUnmarshalerFactory
from .polymorphism.unions import PrimitiveUnionMarshalerFactory
from .polymorphism.unions import PrimitiveUnionUnmarshalerFactory
from .singular.base64 import BASE64_MARSHALER_FACTORY
from .singular.base64 import BASE64_UNMARSHALER_FACTORY
from .singular.datetimes import DATETIME_MARSHALER_FACTORY
from .singular.datetimes import DATETIME_UNMARSHALER_FACTORY
from .singular.enums import EnumMarshalerFactory
from .singular.enums import EnumUnmarshalerFactory
from .singular.numbers import NUMBERS_MARSHALER_FACTORY
from .singular.numbers import NUMBERS_UNMARSHALER_FACTORY
from .singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from .singular.primitives import PRIMITIVE_UNMARSHALER_FACTORY
from .singular.uuids import UUID_MARSHALER_FACTORY
from .singular.uuids import UUID_UNMARSHALER_FACTORY
from .trivial.any import ANY_MARSHALER_FACTORY
from .trivial.any import ANY_UNMARSHALER_FACTORY


##


STANDARD_MARSHALER_FACTORIES: list[MarshalerFactory] = [
    PRIMITIVE_MARSHALER_FACTORY,
    NewtypeMarshalerFactory(),
    OptionalMarshalerFactory(),
    PrimitiveUnionMarshalerFactory(),
    DataclassMarshalerFactory(),
    NamedtupleMarshalerFactory(),
    EnumMarshalerFactory(),
    LiteralMarshalerFactory(),
    NUMBERS_MARSHALER_FACTORY,
    UUID_MARSHALER_FACTORY,
    BASE64_MARSHALER_FACTORY,
    DATETIME_MARSHALER_FACTORY,
    MaybeMarshalerFactory(),
    MappingMarshalerFactory(),
    SequenceNotStrMarshalerFactory(),
    IterableMarshalerFactory(),
    ANY_MARSHALER_FACTORY,
]


def new_standard_marshaler_factory() -> MarshalerFactory:
    return TypeCacheMarshalerFactory(
        RecursiveMarshalerFactory(
            MultiMarshalerFactory(
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
    NamedtupleUnmarshalerFactory(),
    EnumUnmarshalerFactory(),
    LiteralUnmarshalerFactory(),
    NUMBERS_UNMARSHALER_FACTORY,
    UUID_UNMARSHALER_FACTORY,
    BASE64_UNMARSHALER_FACTORY,
    DATETIME_UNMARSHALER_FACTORY,
    MaybeUnmarshalerFactory(),
    MappingUnmarshalerFactory(),
    SequenceNotStrUnmarshalerFactory(),
    IterableUnmarshalerFactory(),
    ANY_UNMARSHALER_FACTORY,
]


def new_standard_unmarshaler_factory() -> UnmarshalerFactory:
    return TypeCacheUnmarshalerFactory(
        RecursiveUnmarshalerFactory(
            MultiUnmarshalerFactory(
                list(STANDARD_UNMARSHALER_FACTORIES),
            ),
        ),
    )


##


def install_standard_factories(
        *factories: MarshalerFactory | UnmarshalerFactory,
) -> None:
    for f in factories:
        k = False

        if isinstance(f, MarshalerFactory):
            STANDARD_MARSHALER_FACTORIES[0:0] = [f]
            k = True

        if isinstance(f, UnmarshalerFactory):
            STANDARD_UNMARSHALER_FACTORIES[0:0] = [f]
            k = True

        if not k:
            raise TypeError(f)
