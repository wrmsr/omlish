"""
FIXME:
 - this is gross and temporary
  - move to global registry somehow
"""
import threading
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
from .composite.unions.literals import LiteralUnionMarshalerFactory
from .composite.unions.literals import LiteralUnionUnmarshalerFactory
from .composite.unions.primitives import PrimitiveUnionMarshalerFactory
from .composite.unions.primitives import PrimitiveUnionUnmarshalerFactory
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


class StandardFactories(ta.NamedTuple):
    marshaler_factories: ta.Sequence[MarshalerFactory]
    unmarshaler_factories: ta.Sequence[UnmarshalerFactory]


DEFAULT_STANDARD_FACTORIES = StandardFactories(
    (
        PRIMITIVE_MARSHALER_FACTORY,
        NewtypeMarshalerFactory(),
        OptionalMarshalerFactory(),
        LiteralUnionMarshalerFactory(),
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
    ),

    (
        PRIMITIVE_UNMARSHALER_FACTORY,
        NewtypeUnmarshalerFactory(),
        OptionalUnmarshalerFactory(),
        LiteralUnionUnmarshalerFactory(),
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
    ),
)


##


def new_standard_marshaler_factory(
        *,
        first: ta.Iterable[MarshalerFactory] | None = None,
        last: ta.Iterable[MarshalerFactory] | None = None,
) -> MarshalerFactory:
    gl: ta.Any = None

    def fi_fn():
        nonlocal gl
        gl = DEFAULT_STANDARD_FACTORIES

        fi: MarshalerFactory = MultiMarshalerFactory(
            *(first if first is not None else []),
            *gl.marshaler_factories,
            *(last if last is not None else []),
        )

        fi = RecursiveMarshalerFactory(fi)

        fi = TypeCacheMarshalerFactory(fi)

        return fi

    fo: MarshalerFactory = (iv := InvalidatableMarshalerFactory(
        fi_fn,
        lambda: DEFAULT_STANDARD_FACTORIES is not gl,
    ))

    fo = ModuleImportingMarshalerFactory(fo, iv.invalidate)

    return fo


def new_standard_unmarshaler_factory(
        *,
        first: ta.Iterable[UnmarshalerFactory] | None = None,
        last: ta.Iterable[UnmarshalerFactory] | None = None,
) -> UnmarshalerFactory:
    gl: ta.Any = None

    def fi_fn():
        nonlocal gl
        gl = DEFAULT_STANDARD_FACTORIES

        fi: UnmarshalerFactory = MultiUnmarshalerFactory(
            *(first if first is not None else []),
            *gl.unmarshaler_factories,
            *(last if last is not None else []),
        )

        fi = RecursiveUnmarshalerFactory(fi)

        fi = TypeCacheUnmarshalerFactory(fi)

        return fi

    fo: UnmarshalerFactory = (iv := InvalidatableUnmarshalerFactory(
        fi_fn,
        lambda: DEFAULT_STANDARD_FACTORIES is not gl,
    ))

    fo = ModuleImportingUnmarshalerFactory(fo, iv.invalidate)

    return fo


##


_GLOBAL_LOCK = threading.RLock()


def install_standard_factories(
        *factories: MarshalerFactory | UnmarshalerFactory,
) -> None:
    with _GLOBAL_LOCK:
        global DEFAULT_STANDARD_FACTORIES

        m_lst: list[MarshalerFactory] = list(DEFAULT_STANDARD_FACTORIES.marshaler_factories)
        u_lst: list[UnmarshalerFactory] = list(DEFAULT_STANDARD_FACTORIES.unmarshaler_factories)

        for f in factories:
            k = False

            if isinstance(f, MarshalerFactory):
                m_lst[0:0] = [f]
                k = True

            if isinstance(f, UnmarshalerFactory):
                u_lst[0:0] = [f]
                k = True

            if not k:
                raise TypeError(f)

        new = StandardFactories(
            tuple(m_lst),
            tuple(u_lst),
        )

        if new != DEFAULT_STANDARD_FACTORIES:
            DEFAULT_STANDARD_FACTORIES = new
