from .... import dataclasses as dc
from .... import lang
from ...base.contexts import MarshalContext
from ...base.contexts import MarshalFactoryContext
from ...base.contexts import UnmarshalContext
from ...base.contexts import UnmarshalFactoryContext
from ...composite.iterables import IterableMarshalerFactory
from ...composite.iterables import IterableUnmarshalerFactory
from ...composite.mappings import MappingMarshalerFactory
from ...composite.mappings import MappingUnmarshalerFactory
from ...composite.optionals import OptionalMarshalerFactory
from ...composite.optionals import OptionalUnmarshalerFactory
from ...factories.multi import MultiMarshalerFactory
from ...factories.multi import MultiUnmarshalerFactory
from ...factories.recursive import RecursiveMarshalerFactory
from ...factories.recursive import RecursiveUnmarshalerFactory
from ...factories.typecache import TypeCacheMarshalerFactory
from ...factories.typecache import TypeCacheUnmarshalerFactory
from ...singular.enums import EnumMarshalerFactory
from ...singular.enums import EnumUnmarshalerFactory
from ...singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from ...singular.primitives import PRIMITIVE_UNMARSHALER_FACTORY
from ..dataclasses import DataclassMarshalerFactory
from ..dataclasses import DataclassUnmarshalerFactory
from ..helpers import update_object_options
from ..namedtuples import NamedtupleMarshalerFactory
from ..namedtuples import NamedtupleUnmarshalerFactory
from ..types import FieldOptions


def _make_test_marshaler_factory():
    return TypeCacheMarshalerFactory(
        RecursiveMarshalerFactory(
            MultiMarshalerFactory(
                PRIMITIVE_MARSHALER_FACTORY,
                OptionalMarshalerFactory(),
                DataclassMarshalerFactory(),
                NamedtupleMarshalerFactory(),
                EnumMarshalerFactory(),
                MappingMarshalerFactory(),
                IterableMarshalerFactory(),
            ),
        ),
    )


def _make_test_unmarshaler_factory():
    return TypeCacheUnmarshalerFactory(
        RecursiveUnmarshalerFactory(
            MultiUnmarshalerFactory(
                PRIMITIVE_UNMARSHALER_FACTORY,
                OptionalUnmarshalerFactory(),
                DataclassUnmarshalerFactory(),
                NamedtupleUnmarshalerFactory(),
                EnumUnmarshalerFactory(),
                MappingUnmarshalerFactory(),
                IterableUnmarshalerFactory(),
            ),
        ),
    )


def test_field_metadata_merge():
    """Test the FieldOptions.merge() method."""

    base = FieldOptions(omit_if=lang.is_none, embed=False)
    override = FieldOptions(embed=True, name='custom')

    merged = base.merge(override)

    # Override values take precedence
    assert merged.embed is True
    assert merged.name == 'custom'

    # Base values preserved when not overridden
    assert merged.omit_if is lang.is_none


def test_field_metadata_merge_with_none():
    """Test merging with None returns original."""

    base = FieldOptions(omit_if=None)
    merged = base.merge(None)

    assert merged is base


def test_omit_if():
    """Test omit_if functionality."""

    @dc.dataclass()
    class Opts:
        a: str
        b: str | None = dc.xfield(None) | dc.field_modifier(lambda f: dc.set_field_metadata(f, {
            FieldOptions: FieldOptions(omit_if=lang.is_none),
        }))

    mfc = MarshalFactoryContext(marshaler_factory=_make_test_marshaler_factory())
    mc = MarshalContext(marshal_factory_context=mfc)

    # With value - should be included
    m1 = mfc.make_marshaler(Opts).marshal(mc, Opts('a', 'b'))
    assert m1 == {'a': 'a', 'b': 'b'}

    # With None - should be omitted
    m2 = mfc.make_marshaler(Opts).marshal(mc, Opts('a', None))
    assert m2 == {'a': 'a'}


def test_field_defaults():
    """Test class-level field defaults."""

    @dc.dataclass(frozen=True)
    @update_object_options(
        field_defaults=FieldOptions(
            omit_if=lang.is_none,
        ),
    )
    class AllOptional:
        a: str | None = None
        b: int | None = None
        c: float | None = None

    mfc = MarshalFactoryContext(marshaler_factory=_make_test_marshaler_factory())
    mc = MarshalContext(marshal_factory_context=mfc)

    # All None - all should be omitted
    m1 = mfc.make_marshaler(AllOptional).marshal(mc, AllOptional())
    assert m1 == {}

    # Some values - only those should appear
    m2 = mfc.make_marshaler(AllOptional).marshal(mc, AllOptional(a='a', c=3.14))
    assert m2 == {'a': 'a', 'c': 3.14}


def test_custom_field_name():
    """Test custom field names with FieldOptions."""

    @dc.dataclass()
    class CustomNames:
        py_name: str = dc.xfield() | dc.field_modifier(lambda f: dc.set_field_metadata(f, {
            FieldOptions: FieldOptions(name='jsonName'),
        }))

    mfc = MarshalFactoryContext(marshaler_factory=_make_test_marshaler_factory())
    mc = MarshalContext(marshal_factory_context=mfc)

    m = mfc.make_marshaler(CustomNames).marshal(mc, CustomNames('value'))
    assert m == {'jsonName': 'value'}

    ufc = UnmarshalFactoryContext(unmarshaler_factory=_make_test_unmarshaler_factory())
    uc = UnmarshalContext(unmarshal_factory_context=ufc)
    u = ufc.make_unmarshaler(CustomNames).unmarshal(uc, {'jsonName': 'value'})

    assert u.py_name == 'value'


def test_field_alts():
    """Test alternative field names for unmarshaling."""

    @dc.dataclass()
    class WithAlts:
        val: str = dc.xfield() | dc.field_modifier(lambda f: dc.set_field_metadata(f, {
            FieldOptions: FieldOptions(name='value', alts=['v', 'val_alt']),
        }))

    ufc = UnmarshalFactoryContext(unmarshaler_factory=_make_test_unmarshaler_factory())
    uc = UnmarshalContext(unmarshal_factory_context=ufc)

    # Should accept primary name
    u1 = ufc.make_unmarshaler(WithAlts).unmarshal(uc, {'value': 'x'})
    assert u1.val == 'x'

    # Should accept alt names
    u2 = ufc.make_unmarshaler(WithAlts).unmarshal(uc, {'v': 'y'})
    assert u2.val == 'y'

    u3 = ufc.make_unmarshaler(WithAlts).unmarshal(uc, {'val_alt': 'z'})
    assert u3.val == 'z'
