# ruff: noqa: PLC0132 SLF001
import dataclasses as dc
import typing as ta

from ...annotations import to_runtime_annotation
from ...core.strconv import type_str
from ...reflect import TypeReflector
from ...universe import TypeUniverse
from ..dataclasses import inspect_dataclass
from ..dataclasses import reflect_dataclass_field_type_keys
from ..members import get_member_call_signature
from ..members import inspect_runtime_members
from ..namedtuples import inspect_namedtuple
from ..namedtuples import reflect_namedtuple_field_type_keys
from ..ops import reflect_is_structural_subtype
from ..ops import reflect_is_structurally_equivalent
from ..ops import reflect_type_key
from ..protocols import check_protocol_implementation
from ..protocols import inspect_protocol_members
from ..protocols import is_protocol_implemented_by
from ..queries import get_runtime_type_shape
from ..queries import reflect_literal_value_type
from ..queries import reflect_mapping_base_args
from ..queries import reflect_optional_item
from ..records import RUNTIME_RECORD_KIND_DATACLASS
from ..records import RUNTIME_RECORD_KIND_NAMEDTUPLE
from ..records import inspect_record


def _make_reflector() -> TypeReflector:
    return TypeReflector(TypeUniverse(dynamic_type_name_suffix='counter'))


def test_runtime_surface_uses_shared_reflector_across_entrypoints() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    class Pair(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        left: t_var  # type: ignore
        right: list[t_var]  # type: ignore

    reflector = _make_reflector()

    dataclass_inspection = inspect_dataclass(Box[int], reflector)  # type: ignore
    namedtuple_inspection = inspect_namedtuple(Pair[str], reflector)  # type: ignore

    assert dataclass_inspection.field_annotations == {'value': int}
    assert namedtuple_inspection.field_annotations == {'left': str, 'right': list[str]}

    assert reflect_dataclass_field_type_keys(Box[int], reflector) == {  # type: ignore
        'value': reflect_type_key(int, reflector),
    }
    assert reflect_namedtuple_field_type_keys(Pair[str], reflector) == {  # type: ignore
        'left': reflect_type_key(str, reflector),
        'right': reflect_type_key(list[str], reflector),
    }

    dataclass_record = inspect_record(Box[int], reflector)  # type: ignore
    namedtuple_record = inspect_record(Pair[str], reflector)  # type: ignore

    assert inspect_dataclass(Box[int], reflector) is dataclass_inspection  # type: ignore
    assert inspect_namedtuple(Pair[str], reflector) is namedtuple_inspection  # type: ignore
    assert inspect_record(Box[int], reflector) is dataclass_record  # type: ignore

    assert dataclass_record.kind == RUNTIME_RECORD_KIND_DATACLASS
    assert namedtuple_record.kind == RUNTIME_RECORD_KIND_NAMEDTUPLE
    assert [field.name for field in dataclass_record.fields] == ['value']
    assert [field.name for field in namedtuple_record.fields] == ['left', 'right']

    optional_item = reflect_optional_item(int | None, reflector)
    mapping_args = reflect_mapping_base_args(dict[str, int], dict, reflector)
    literal_info = reflect_literal_value_type(ta.Literal['a', 'b'], reflector)

    assert optional_item is not None
    assert type_str(optional_item) == 'builtins.int'
    assert mapping_args is not None
    assert [type_str(arg) for arg in mapping_args] == ['builtins.str', 'builtins.int']
    assert literal_info is not None
    assert literal_info.values == ('a', 'b')

    assert to_runtime_annotation(reflector.reflect_type(list[int]), reflector.universe) == list[int]


def test_runtime_surface_includes_member_protocol_and_protocol_check_apis() -> None:
    class Reader(ta.Protocol):
        @property
        def name(self) -> object:
            ...

        def read(self, size: int, *, strict: bool = False) -> bytes:
            ...

    class Concrete:
        @property
        def name(self) -> str:
            return ''

        def read(self, size: int, *, strict: bool = False) -> bytes:
            return b''

    reflector = _make_reflector()

    members = inspect_runtime_members(Concrete, reflector)
    protocol = inspect_protocol_members(Reader, reflector)

    read_signature = get_member_call_signature(members.members_by_name['read'])
    assert read_signature is not None
    read_parameters = [
        (parameter.name, parameter.kind.name, parameter.has_default)
        for parameter in read_signature.parameters
    ]
    assert read_parameters == [
        ('size', 'POSITIONAL_OR_KEYWORD', False),
        ('strict', 'KEYWORD_ONLY', True),
    ]

    assert set(protocol.members_by_name) == {'name', 'read'}
    assert is_protocol_implemented_by(Concrete, Reader, reflector)
    assert check_protocol_implementation(Concrete, Reader, reflector) == []
    assert inspect_runtime_members(Concrete, reflector) is members
    assert inspect_protocol_members(Reader, reflector) is protocol


def test_runtime_surface_handles_new_type_literal_workflow() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class ModeBox(Box[mode]):  # type: ignore
        pass

    class ModeService:
        def set_mode(self, mode: mode) -> mode:
            return mode

    class HasMode(ta.Protocol):
        value: ta.Any

        def set_mode(self, mode: mode) -> mode:
            ...

    HasMode.__annotations__['value'] = mode

    @dc.dataclass
    class Concrete:
        value: ta.Any

        def set_mode(self, mode: mode) -> mode:
            return mode

    Concrete.__annotations__['value'] = mode

    reflector = _make_reflector()
    mode_type = reflector.reflect_type(mode)
    other_mode_type = reflector.reflect_type(other_mode)

    dataclass_inspection = inspect_dataclass(ModeBox, reflector)
    [field] = dataclass_inspection.fields
    field_shape = get_runtime_type_shape(field.replaced_type, reflector)

    assert dataclass_inspection.field_annotations == {'value': mode}
    assert reflector.to_runtime_annotation(field.replaced_type) is mode
    assert field_shape.new_type is not None
    assert field_shape.new_type.obj is mode
    assert field_shape.literal_value_type is not None
    assert field_shape.literal_value_type.values == ('a', 'b')

    member = inspect_runtime_members(ModeService, reflector).members_by_name['set_mode']
    signature = get_member_call_signature(member)
    assert signature is not None
    assert reflector.to_runtime_annotation(signature.parameters[0].typ) is mode
    assert reflector.to_runtime_annotation(signature.return_type) is mode

    protocol = inspect_protocol_members(HasMode, reflector)
    assert protocol.member_keys['value'] == reflect_type_key(mode, reflector)
    assert is_protocol_implemented_by(Concrete, HasMode, reflector)
    assert check_protocol_implementation(Concrete, HasMode, reflector) == []

    assert reflect_type_key(mode, reflector) != reflect_type_key(other_mode, reflector)
    assert reflector.reflect_type(mode) is mode_type
    assert reflector.type_key(mode_type) is reflector.type_key(mode_type)
    assert reflector.type_key(other_mode_type) is reflector.type_key(other_mode_type)
    assert inspect_dataclass(ModeBox, reflector) is dataclass_inspection


def test_runtime_surface_preserves_alias_identity_but_exposes_structural_comparison() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    @dc.dataclass
    class Config:
        modes: mode_list  # type: ignore

    class HasModes(ta.Protocol):
        modes: list[mode]  # noqa

    reflector = _make_reflector()

    inspection = inspect_dataclass(Config, reflector)
    field = inspection.fields_by_name['modes']
    shape = get_runtime_type_shape(field.replaced_type, reflector)

    assert shape.alias is not None
    assert shape.alias.obj is mode_list
    assert reflector.to_runtime_annotation(field.replaced_type) == list[mode]  # noqa
    assert reflector.to_runtime_annotation(
        field.replaced_type,
        type_alias_policy='preserve',
    ) is mode_list
    assert reflect_type_key(mode_list, reflector) != reflect_type_key(list[mode], reflector)  # noqa
    assert reflect_is_structurally_equivalent(mode_list, list[mode], reflector)  # noqa
    assert reflect_is_structural_subtype(mode_list, list[mode], reflector)  # noqa
    assert reflect_is_structural_subtype(list[mode], mode_list, reflector)  # noqa
    assert is_protocol_implemented_by(Config, HasModes, reflector)
