"""
FIXME:
 - lock lol
  - probably move to global registry somehow
"""
import typing as ta

from .base.types import MarshalerFactory
from .base.types import UnmarshalerFactory
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
from .factories.invalidate import InvalidatableMarshalerFactory
from .factories.invalidate import InvalidatableUnmarshalerFactory
from .factories.moduleimport.factories import ModuleImportingMarshalerFactory
from .factories.moduleimport.factories import ModuleImportingUnmarshalerFactory
from .factories.multi import MultiMarshalerFactory
from .factories.multi import MultiUnmarshalerFactory
from .factories.recursive import RecursiveMarshalerFactory
from .factories.recursive import RecursiveUnmarshalerFactory
from .factories.typecache import TypeCacheMarshalerFactory
from .factories.typecache import TypeCacheUnmarshalerFactory
from .objects.dataclasses import DataclassMarshalerFactory
from .objects.dataclasses import DataclassUnmarshalerFactory
from .objects.namedtuples import NamedtupleMarshalerFactory
from .objects.namedtuples import NamedtupleUnmarshalerFactory
from .polymorphism.unions import PrimitiveUnionMarshalerFactory
from .polymorphism.unions import PrimitiveUnionUnmarshalerFactory
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


DEFAULT_STANDARD_MARSHALER_FACTORIES: ta.Sequence[MarshalerFactory] = [
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
    DATETIME_MARSHALER_FACTORY,
    MaybeMarshalerFactory(),
    MappingMarshalerFactory(),
    SequenceNotStrMarshalerFactory(),
    IterableMarshalerFactory(),
    ANY_MARSHALER_FACTORY,
]


DEFAULT_STANDARD_UNMARSHALER_FACTORIES: ta.Sequence[UnmarshalerFactory] = [
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
    DATETIME_UNMARSHALER_FACTORY,
    MaybeUnmarshalerFactory(),
    MappingUnmarshalerFactory(),
    SequenceNotStrUnmarshalerFactory(),
    IterableUnmarshalerFactory(),
    ANY_UNMARSHALER_FACTORY,
]


##


def new_standard_marshaler_factory(
        *,
        first: ta.Iterable[MarshalerFactory] | None = None,
        last: ta.Iterable[MarshalerFactory] | None = None,
) -> MarshalerFactory:
    f: MarshalerFactory = MultiMarshalerFactory([
        *(first if first is not None else []),
        *DEFAULT_STANDARD_MARSHALER_FACTORIES,
        *(last if last is not None else []),
    ])

    f = RecursiveMarshalerFactory(f)
    f = TypeCacheMarshalerFactory(f)
    f = ModuleImportingMarshalerFactory(f)

    return f


def new_standard_unmarshaler_factory(
        *,
        first: ta.Iterable[UnmarshalerFactory] | None = None,
        last: ta.Iterable[UnmarshalerFactory] | None = None,
) -> UnmarshalerFactory:
    f: UnmarshalerFactory = MultiUnmarshalerFactory([
        *(first if first is not None else []),
        *DEFAULT_STANDARD_UNMARSHALER_FACTORIES,
        *(last if last is not None else []),
    ])

    f = RecursiveUnmarshalerFactory(f)
    f = TypeCacheUnmarshalerFactory(f)
    f = ModuleImportingUnmarshalerFactory(f)

    return f


##


def install_standard_factories(
        *factories: MarshalerFactory | UnmarshalerFactory,
) -> None:
    for f in factories:
        k = False

        if isinstance(f, MarshalerFactory):
            DEFAULT_STANDARD_MARSHALER_FACTORIES[0:0] = [f]
            k = True

        if isinstance(f, UnmarshalerFactory):
            DEFAULT_STANDARD_UNMARSHALER_FACTORIES[0:0] = [f]
            k = True

        if not k:
            raise TypeError(f)
