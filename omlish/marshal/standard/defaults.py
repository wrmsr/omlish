# flake8: noqa: E241
import typing as ta

from ..api.types import MarshalerFactory
from ..api.types import UnmarshalerFactory
from ..composite.iterables import IterableMarshalerFactory
from ..composite.iterables import IterableUnmarshalerFactory
from ..composite.literals import LiteralMarshalerFactory
from ..composite.literals import LiteralUnmarshalerFactory
from ..composite.mappings import MappingMarshalerFactory
from ..composite.mappings import MappingUnmarshalerFactory
from ..composite.maybes import MaybeMarshalerFactory
from ..composite.maybes import MaybeUnmarshalerFactory
from ..composite.newtypes import NewtypeMarshalerFactory
from ..composite.newtypes import NewtypeUnmarshalerFactory
from ..composite.optionals import OptionalMarshalerFactory
from ..composite.optionals import OptionalUnmarshalerFactory
from ..composite.special import SequenceNotStrMarshalerFactory
from ..composite.special import SequenceNotStrUnmarshalerFactory
from ..composite.unions.literals import LiteralUnionMarshalerFactory
from ..composite.unions.literals import LiteralUnionUnmarshalerFactory
from ..composite.unions.primitives import PrimitiveUnionMarshalerFactory
from ..composite.unions.primitives import PrimitiveUnionUnmarshalerFactory
from ..objects.dataclasses import DataclassMarshalerFactory
from ..objects.dataclasses import DataclassUnmarshalerFactory
from ..objects.namedtuples import NamedtupleMarshalerFactory
from ..objects.namedtuples import NamedtupleUnmarshalerFactory
from ..singular.datetimes import DATETIME_MARSHALER_FACTORY
from ..singular.datetimes import DATETIME_UNMARSHALER_FACTORY
from ..singular.enums import EnumMarshalerFactory
from ..singular.enums import EnumUnmarshalerFactory
from ..singular.numbers import NUMBERS_MARSHALER_FACTORY
from ..singular.numbers import NUMBERS_UNMARSHALER_FACTORY
from ..singular.opaquerepr import OPAQUE_REPR_MARSHALER_FACTORY
from ..singular.opaquerepr import OPAQUE_REPR_UNMARSHALER_FACTORY
from ..singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from ..singular.primitives import PRIMITIVE_UNMARSHALER_FACTORY
from ..singular.uuids import UUID_MARSHALER_FACTORY
from ..singular.uuids import UUID_UNMARSHALER_FACTORY
from ..trivial.any import ANY_MARSHALER_FACTORY
from ..trivial.any import ANY_UNMARSHALER_FACTORY
from ..typedvalues.collections import TypedValuesMarshalerFactory
from ..typedvalues.collections import TypedValuesUnmarshalerFactory
from ..typedvalues.unions import TypedValueUnionMarshalerFactory
from ..typedvalues.unions import TypedValueUnionUnmarshalerFactory
from ..typedvalues.values import TypedValueMarshalerFactory
from ..typedvalues.values import TypedValueUnmarshalerFactory


##


@ta.final
class DefaultStandardFactories(ta.NamedTuple):
    marshaler_factories: ta.Sequence[MarshalerFactory]
    unmarshaler_factories: ta.Sequence[UnmarshalerFactory]

    @classmethod
    def of_pairs(
            cls,
            pairs: ta.Sequence[
                tuple[
                    MarshalerFactory | None,
                    UnmarshalerFactory | None,
                ],
            ],
    ) -> DefaultStandardFactories:
        return cls(
            tuple(mf for mf, _ in pairs if mf is not None),
            tuple(uf for _, uf in pairs if uf is not None),
        )


DEFAULT_STANDARD_FACTORIES: ta.Final = DefaultStandardFactories.of_pairs([
    (OPAQUE_REPR_MARSHALER_FACTORY,     OPAQUE_REPR_UNMARSHALER_FACTORY),
    (PRIMITIVE_MARSHALER_FACTORY,       PRIMITIVE_UNMARSHALER_FACTORY),
    (NewtypeMarshalerFactory(),         NewtypeUnmarshalerFactory()),
    (OptionalMarshalerFactory(),        OptionalUnmarshalerFactory()),
    (LiteralUnionMarshalerFactory(),    LiteralUnionUnmarshalerFactory()),
    (TypedValueMarshalerFactory(),      TypedValueUnmarshalerFactory()),
    (TypedValueUnionMarshalerFactory(), TypedValueUnionUnmarshalerFactory()),
    (TypedValuesMarshalerFactory(),     TypedValuesUnmarshalerFactory()),
    (PrimitiveUnionMarshalerFactory(),  PrimitiveUnionUnmarshalerFactory()),
    (DataclassMarshalerFactory(),       DataclassUnmarshalerFactory()),
    (NamedtupleMarshalerFactory(),      NamedtupleUnmarshalerFactory()),
    (EnumMarshalerFactory(),            EnumUnmarshalerFactory()),
    (LiteralMarshalerFactory(),         LiteralUnmarshalerFactory()),
    (NUMBERS_MARSHALER_FACTORY,         NUMBERS_UNMARSHALER_FACTORY),
    (UUID_MARSHALER_FACTORY,            UUID_UNMARSHALER_FACTORY),
    (DATETIME_MARSHALER_FACTORY,        DATETIME_UNMARSHALER_FACTORY),
    (MaybeMarshalerFactory(),           MaybeUnmarshalerFactory()),
    (MappingMarshalerFactory(),         MappingUnmarshalerFactory()),
    (SequenceNotStrMarshalerFactory(),  SequenceNotStrUnmarshalerFactory()),
    (IterableMarshalerFactory(),        IterableUnmarshalerFactory()),
    (ANY_MARSHALER_FACTORY,             ANY_UNMARSHALER_FACTORY),
])
