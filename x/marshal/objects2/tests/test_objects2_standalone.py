"""
Standalone tests for objects2 refactored code.

Tests the new architecture directly using objects2 factories, independent of the global marshal system.
"""
# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.lite import marshal as lmsh
from omlish.marshal.base.contexts import MarshalContext
from omlish.marshal.base.contexts import MarshalFactoryContext
from omlish.marshal.base.contexts import UnmarshalContext
from omlish.marshal.base.contexts import UnmarshalFactoryContext
from omlish.marshal.base.types import MarshalerFactory
from omlish.marshal.base.types import UnmarshalerFactory
from omlish.marshal.composite.iterables import IterableMarshalerFactory
from omlish.marshal.composite.iterables import IterableUnmarshalerFactory
from omlish.marshal.composite.mappings import MappingMarshalerFactory
from omlish.marshal.composite.mappings import MappingUnmarshalerFactory
from omlish.marshal.composite.optionals import OptionalMarshalerFactory
from omlish.marshal.composite.optionals import OptionalUnmarshalerFactory
from omlish.marshal.factories.multi import MultiMarshalerFactory
from omlish.marshal.factories.multi import MultiUnmarshalerFactory
from omlish.marshal.factories.recursive import RecursiveMarshalerFactory
from omlish.marshal.factories.recursive import RecursiveUnmarshalerFactory
from omlish.marshal.factories.typecache import TypeCacheMarshalerFactory
from omlish.marshal.factories.typecache import TypeCacheUnmarshalerFactory
from omlish.marshal.singular.enums import EnumMarshalerFactory
from omlish.marshal.singular.enums import EnumUnmarshalerFactory
from omlish.marshal.singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from omlish.marshal.singular.primitives import PRIMITIVE_UNMARSHALER_FACTORY
from omlish.marshal.trivial.nop import NOP_MARSHALER_UNMARSHALER

from ..dataclasses import DataclassMarshalerFactory
from ..dataclasses import DataclassUnmarshalerFactory
from ..helpers import update_fields_metadata
from ..helpers import update_object_metadata
from ..marshal import ObjectMarshaler
from ..metadata import FieldInfo
from ..metadata import FieldMetadata
from ..metadata import ObjectSpecials
from ..namedtuples import NamedtupleMarshalerFactory
from ..namedtuples import NamedtupleUnmarshalerFactory
from ..unmarshal import ObjectUnmarshaler


def _make_test_marshaler_factory():
    """
    Create a test marshaler factory with objects2 components.

    Stack: TypeCache -> Recursive -> Multi -> [primitives, objects2 dataclass, etc.]
    """
    mf: MarshalerFactory = TypeCacheMarshalerFactory(
        RecursiveMarshalerFactory(
            MultiMarshalerFactory(
                PRIMITIVE_MARSHALER_FACTORY,
                OptionalMarshalerFactory(),
                DataclassMarshalerFactory(),  # objects2 version
                NamedtupleMarshalerFactory(),  # objects2 version
                EnumMarshalerFactory(),
                MappingMarshalerFactory(),
                IterableMarshalerFactory(),
            ),
        ),
    )
    return mf


def _make_test_unmarshaler_factory():
    """
    Create a test unmarshaler factory with objects2 components.

    Stack: TypeCache -> Recursive -> Multi -> [primitives, objects2 dataclass, etc.]
    """
    uf: UnmarshalerFactory = TypeCacheUnmarshalerFactory(
        RecursiveUnmarshalerFactory(
            MultiUnmarshalerFactory(
                PRIMITIVE_UNMARSHALER_FACTORY,
                OptionalUnmarshalerFactory(),
                DataclassUnmarshalerFactory(),  # objects2 version
                NamedtupleUnmarshalerFactory(),  # objects2 version
                EnumUnmarshalerFactory(),
                MappingUnmarshalerFactory(),
                IterableUnmarshalerFactory(),
            ),
        ),
    )
    return uf


##


@dc.dataclass()
class C:
    i: int
    s: str
    x: dict[str, ta.Any]


def test_unknown_fields():
    fis = [
        FieldInfo(
            name='i',
            type=int,
            marshal_name='i',
            unmarshal_names=['i'],
        ),
        FieldInfo(
            name='s',
            type=str,
            marshal_name='s',
            unmarshal_names=['s'],
        ),
    ]

    ou = ObjectUnmarshaler(
        C,
        {fi.name: (fi, NOP_MARSHALER_UNMARSHALER) for fi in fis},
        specials=ObjectSpecials(unknown='x'),
    )
    uc = UnmarshalContext(unmarshal_factory_context=UnmarshalFactoryContext())
    c = ou.unmarshal(uc, {'i': 420, 's': 'foo', 'qqq': 'huh'})
    assert c == C(i=420, s='foo', x={'qqq': 'huh'})

    om = ObjectMarshaler(
        [(fi, NOP_MARSHALER_UNMARSHALER) for fi in fis],
        specials=ObjectSpecials(unknown='x'),
    )
    mc = MarshalContext(marshal_factory_context=MarshalFactoryContext())
    o = om.marshal(mc, c)
    assert o == {'i': 420, 's': 'foo', 'qqq': 'huh'}


def test_decorated_unknown_field():
    """Test unknown_field metadata with objects2 factories."""

    @dc.dataclass(frozen=True)
    @update_object_metadata(unknown_field='x')
    class ImageUploadResponse:
        status: int
        success: bool

        x: ta.Mapping[str, ta.Any] | None = None

    d = {
        'status': 420,
        'success': True,
        'barf': True,
        'frab': False,
    }

    ufc = UnmarshalFactoryContext(unmarshaler_factory=_make_test_unmarshaler_factory())
    u = ufc.make_unmarshaler(ImageUploadResponse)

    uc = UnmarshalContext(unmarshal_factory_context=ufc)
    o = u.unmarshal(uc, d)

    assert o == ImageUploadResponse(
        status=420,
        success=True,
        x=dict(
            barf=True,
            frab=False,
        ),
    )


def test_source_fields():
    fis = [
        FieldInfo(
            name='i',
            type=int,
            marshal_name='i',
            unmarshal_names=['i'],
        ),
        FieldInfo(
            name='s',
            type=str,
            marshal_name='s',
            unmarshal_names=['s'],
        ),
    ]

    ou = ObjectUnmarshaler(
        C,
        {fi.name: (fi, NOP_MARSHALER_UNMARSHALER) for fi in fis},
        specials=ObjectSpecials(source='x'),
        ignore_unknown=True,
    )
    uc = UnmarshalContext(unmarshal_factory_context=UnmarshalFactoryContext())
    c = ou.unmarshal(uc, {'i': 420, 's': 'foo', 'qqq': 'huh'})
    assert c == C(i=420, s='foo', x={'i': 420, 's': 'foo', 'qqq': 'huh'})

    om = ObjectMarshaler(
        [(fi, NOP_MARSHALER_UNMARSHALER) for fi in fis],
        specials=ObjectSpecials(source='x'),
    )
    mc = MarshalContext(marshal_factory_context=MarshalFactoryContext())
    o = om.marshal(mc, c)
    assert o == {'i': 420, 's': 'foo'}


##


@dc.dataclass()
class E0:
    i: int


@dc.dataclass()
class E1:
    s: str


@dc.dataclass()
class E2:
    f: float


@dc.dataclass()
@update_fields_metadata(['e1'], embed=True)
@update_fields_metadata(['e2'], embed=True, name='')
class E3:
    e0: E0
    e1: E1
    e2: E2
    b: bool


def test_embed():
    """Test embedded fields with objects2 factories."""
    o = E3(
        E0(420),
        E1('ft'),
        E2(4.2),
        True,
    )

    # Use objects2 factories
    mfc = MarshalFactoryContext(marshaler_factory=_make_test_marshaler_factory())
    mc = MarshalContext(marshal_factory_context=mfc)
    m = mfc.make_marshaler(E3).marshal(mc, o)
    print(m)

    ufc = UnmarshalFactoryContext(unmarshaler_factory=_make_test_unmarshaler_factory())
    uc = UnmarshalContext(unmarshal_factory_context=ufc)
    u = ufc.make_unmarshaler(E3).unmarshal(uc, m)

    assert u == o


##


class Pt(ta.NamedTuple):
    i: int
    f: float
    s: str = 'foo'


def test_namedtuples():
    """Test namedtuples with objects2 factories."""
    p = Pt(1, 2.)

    mfc = MarshalFactoryContext(marshaler_factory=_make_test_marshaler_factory())
    mc = MarshalContext(marshal_factory_context=mfc)
    d = mfc.make_marshaler(Pt).marshal(mc, p)

    assert d == {'i': 1, 'f': 2., 's': 'foo'}

    ufc = UnmarshalFactoryContext(unmarshaler_factory=_make_test_unmarshaler_factory())
    uc = UnmarshalContext(unmarshal_factory_context=ufc)
    u = ufc.make_unmarshaler(Pt).unmarshal(uc, d)

    assert u == p


##


def test_lite_name_overrides():
    """Test lite marshal compatibility for field name overrides."""

    @dc.dataclass
    class Junk:
        a: str
        b: str = dc.field(metadata={lmsh.OBJ_MARSHALER_FIELD_KEY: 'b!'})
        c: str = dc.field(default='default c', metadata={lmsh.OBJ_MARSHALER_FIELD_KEY: None})

    j = Junk('a', 'b', 'c')

    mfc = MarshalFactoryContext(marshaler_factory=_make_test_marshaler_factory())
    mc = MarshalContext(marshal_factory_context=mfc)
    m = mfc.make_marshaler(Junk).marshal(mc, j)

    assert m == {'a': 'a', 'b!': 'b'}

    ufc = UnmarshalFactoryContext(unmarshaler_factory=_make_test_unmarshaler_factory())
    uc = UnmarshalContext(unmarshal_factory_context=ufc)
    u: Junk = ufc.make_unmarshaler(Junk).unmarshal(uc, m)

    assert u == Junk('a', 'b', 'default c')


def test_lite_omit_if_none():
    """Test lite marshal compatibility for omit_if_none."""

    @dc.dataclass
    class Junk:
        a: str
        b: ta.Optional[str]
        c: ta.Optional[str] = dc.field(metadata={lmsh.OBJ_MARSHALER_OMIT_IF_NONE: True})

    mfc = MarshalFactoryContext(marshaler_factory=_make_test_marshaler_factory())
    mc = MarshalContext(marshal_factory_context=mfc)

    m1 = mfc.make_marshaler(Junk).marshal(mc, Junk('a', 'b', 'c'))
    assert m1 == {'a': 'a', 'b': 'b', 'c': 'c'}

    m2 = mfc.make_marshaler(Junk).marshal(mc, Junk('a', None, None))
    assert m2 == {'a': 'a', 'b': None}


##


def test_field_metadata_merge():
    """Test the FieldMetadata.merge() method."""
    base = FieldMetadata(omit_if=lang.is_none, embed=False)
    override = FieldMetadata(embed=True, name='custom')

    merged = base.merge(override)

    # Override values take precedence
    assert merged.embed is True
    assert merged.name == 'custom'

    # Base values preserved when not overridden
    assert merged.omit_if is lang.is_none


def test_field_metadata_merge_with_none():
    """Test merging with None returns original."""
    base = FieldMetadata(omit_if=lang.is_none)
    merged = base.merge(None)

    assert merged is base


def test_omit_if():
    """Test omit_if functionality."""

    @dc.dataclass()
    class Opts:
        a: str
        b: str | None = dc.xfield(None) | dc.field_modifier(lambda f: dc.set_field_metadata(f, {
            FieldMetadata: FieldMetadata(omit_if=lang.is_none),
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
    @update_object_metadata(
        field_defaults=FieldMetadata(
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
    """Test custom field names with FieldMetadata."""

    @dc.dataclass()
    class CustomNames:
        py_name: str = dc.xfield() | dc.field_modifier(lambda f: dc.set_field_metadata(f, {
            FieldMetadata: FieldMetadata(name='jsonName'),
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
            FieldMetadata: FieldMetadata(name='value', alts=['v', 'val_alt']),
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
