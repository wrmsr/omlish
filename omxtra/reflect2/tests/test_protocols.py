# ruff: noqa: F821 PLC0132 SLF001
import dataclasses as dc
import inspect
import typing as ta

import pytest

from ..core import types
from ..core.strconv import type_str
from ..errors import ReflectionError
from ..members import RuntimeMember
from ..members import RuntimeMemberKind
from ..members import get_member_call_signature
from ..members import get_member_call_signature_key
from ..members import get_member_call_structural_signature_key
from ..members import get_member_value_structural_type_key
from ..members import get_member_value_type
from ..members import inspect_runtime_members
from ..protocols import get_protocol_member_key
from ..protocols import get_protocol_member_structural_key
from ..protocols import inspect_protocol_members
from ..protocols import is_protocol
from ..queries import get_runtime_collection_shape
from ..queries import get_runtime_type_shape
from ..records import inspect_record
from ..reflect import RuntimeTypeReflector
from ..universe import RuntimeTypeUniverse


def test_is_protocol_detects_typing_protocol_classes() -> None:
    class Reader(ta.Protocol):
        def read(self) -> bytes:
            ...

    class Concrete:
        pass

    assert is_protocol(Reader)
    assert not is_protocol(Concrete)


def test_inspect_protocol_members_collects_method_signature() -> None:
    class Reader(ta.Protocol):
        def read(self) -> bytes:
            ...

    member = inspect_protocol_members(Reader).members_by_name['read']
    call_signature = get_member_call_signature(member)

    assert member.kind == RuntimeMemberKind.FUNCTION
    assert call_signature is not None
    assert call_signature.parameters == ()
    assert type_str(call_signature.return_type) == 'builtins.bytes'


def test_inspect_protocol_members_cache_is_per_reflector() -> None:
    class Reader(ta.Protocol):
        def read(self) -> bytes:
            ...

    left_reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    right_reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    left = inspect_protocol_members(Reader, left_reflector)

    assert inspect_protocol_members(Reader, left_reflector) is left
    assert inspect_protocol_members(Reader, right_reflector) is not left


def test_protocol_method_key_matches_equivalent_concrete_method_key() -> None:
    class Reader(ta.Protocol):
        def read(self) -> bytes:
            ...

    class Concrete:
        def read(self) -> bytes:
            return b''

    protocol_member = inspect_protocol_members(Reader).members_by_name['read']
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    concrete_member = inspect_runtime_members(Concrete, reflector).members_by_name['read']

    assert get_protocol_member_key(protocol_member) == get_member_call_signature_key(concrete_member)


def test_protocol_method_structural_key_matches_alias_expanded_concrete_method_key() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    class HasModes(ta.Protocol):
        def set_modes(self, modes: mode_list) -> mode_list:  # type: ignore
            ...

    class Concrete:
        def set_modes(self, modes: list[mode]) -> list[mode]:  # noqa
            return modes

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    protocol_member = inspect_protocol_members(HasModes, reflector).members_by_name['set_modes']
    concrete_member = inspect_runtime_members(Concrete, reflector).members_by_name['set_modes']

    assert get_protocol_member_key(protocol_member, reflector) == get_member_call_signature_key(
        concrete_member,
        reflector,
    )
    assert get_protocol_member_structural_key(protocol_member, reflector) == get_member_call_structural_signature_key(
        concrete_member,
        reflector,
    )
    assert inspect_protocol_members(HasModes, reflector).member_structural_keys['set_modes'] == (
        get_protocol_member_structural_key(protocol_member, reflector)
    )


def test_inspect_protocol_members_collects_annotated_data_member() -> None:
    class HasName(ta.Protocol):
        name: str

    member = inspect_protocol_members(HasName).members_by_name['name']
    value_type = get_member_value_type(member)

    assert member.kind == RuntimeMemberKind.DATA
    assert value_type is not None
    assert type_str(value_type) == 'builtins.str'


def test_inspect_protocol_members_preserves_literal_new_type_method_signature() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    class HasMode(ta.Protocol):
        def set_mode(self, mode: mode) -> mode:
            ...

    member = inspect_protocol_members(HasMode, reflector).members_by_name['set_mode']
    signature = get_member_call_signature(member)

    assert signature is not None
    assert reflector.to_runtime_annotation(signature.parameters[0].typ) is mode
    assert reflector.to_runtime_annotation(signature.return_type) is mode
    parameter_shape = get_runtime_type_shape(signature.parameters[0].typ, reflector)
    return_shape = get_runtime_type_shape(signature.return_type, reflector)
    assert parameter_shape.new_type is not None
    assert parameter_shape.new_type.obj is mode
    assert parameter_shape.literal_value_type is not None
    assert parameter_shape.literal_value_type.values == ('a', 'b')
    assert return_shape.new_type is not None
    assert return_shape.new_type.obj is mode
    assert return_shape.literal_value_type is not None
    assert return_shape.literal_value_type.values == ('a', 'b')


def test_inspect_protocol_members_preserves_literal_new_type_data_member() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    class HasMode(ta.Protocol):
        mode: ta.Any

    HasMode.__annotations__['mode'] = mode

    member = inspect_protocol_members(HasMode, reflector).members_by_name['mode']
    value_type = get_member_value_type(member)

    assert value_type is not None
    assert reflector.to_runtime_annotation(value_type) is mode
    shape = get_runtime_type_shape(value_type, reflector)
    assert shape.new_type is not None
    assert shape.new_type.obj is mode
    assert shape.literal_value_type is not None
    assert shape.literal_value_type.values == ('a', 'b')


def test_inspect_protocol_members_expands_alias_new_type_literal_method_signature() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    class HasModes(ta.Protocol):
        def set_modes(self, modes: mode_list) -> mode_list:  # type: ignore
            ...

    member = inspect_protocol_members(HasModes, reflector).members_by_name['set_modes']
    signature = get_member_call_signature(member)

    assert signature is not None
    assert reflector.to_runtime_annotation(signature.parameters[0].typ) == list[mode]  # noqa
    assert reflector.to_runtime_annotation(signature.return_type) == list[mode]  # noqa
    collection_shape = get_runtime_collection_shape(signature.parameters[0].typ, reflector)
    assert collection_shape.sequence_item is not None
    item_shape = get_runtime_type_shape(collection_shape.sequence_item, reflector)
    assert item_shape.new_type is not None
    assert item_shape.new_type.obj is mode
    assert item_shape.literal_value_type is not None
    assert item_shape.literal_value_type.values == ('a', 'b')


def test_inspect_protocol_members_expands_alias_new_type_literal_data_member() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    class HasModes(ta.Protocol):
        modes: ta.Any

    HasModes.__annotations__['modes'] = mode_list

    member = inspect_protocol_members(HasModes, reflector).members_by_name['modes']
    value_type = get_member_value_type(member)

    assert value_type is not None
    assert reflector.to_runtime_annotation(value_type) == list[mode]  # noqa
    collection_shape = get_runtime_collection_shape(value_type, reflector)
    assert collection_shape.sequence_item is not None
    item_shape = get_runtime_type_shape(collection_shape.sequence_item, reflector)
    assert item_shape.new_type is not None
    assert item_shape.new_type.obj is mode
    assert item_shape.literal_value_type is not None
    assert item_shape.literal_value_type.values == ('a', 'b')


def test_protocol_data_member_key_matches_concrete_record_field_key() -> None:
    class HasName(ta.Protocol):
        name: str

    @dc.dataclass
    class Concrete:
        name: str

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    protocol_inspection = inspect_protocol_members(HasName, reflector)
    record_inspection = inspect_record(Concrete, reflector)

    assert protocol_inspection.member_keys['name'] == record_inspection.fields_by_name['name'].type_key


def test_protocol_data_member_structural_key_matches_recursive_alias_unrolled_record_field_key() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore

    class HasNode(ta.Protocol):
        node: alias  # type: ignore

    @dc.dataclass
    class Concrete:
        node: int | list[alias]  # type: ignore

    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )
    protocol_inspection = inspect_protocol_members(HasNode, reflector)
    record_inspection = inspect_record(Concrete, reflector)
    protocol_member = protocol_inspection.members_by_name['node']
    concrete_member = inspect_runtime_members(Concrete, reflector).members_by_name.get('node')

    assert concrete_member is None
    assert protocol_inspection.member_structural_keys['node'] == (
        record_inspection.fields_by_name['node'].structural_type_key
    )
    assert get_protocol_member_structural_key(protocol_member, reflector) == (
        record_inspection.fields_by_name['node'].structural_type_key
    )


def test_protocol_data_member_structural_key_preserves_new_type_identity() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore

    class HasMode(ta.Protocol):
        mode: ta.Any

    HasMode.__annotations__['mode'] = mode

    @dc.dataclass
    class Concrete:
        mode: ta.Any

    Concrete.__annotations__['mode'] = other_mode

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    protocol_member = inspect_protocol_members(HasMode, reflector).members_by_name['mode']
    concrete_member = inspect_record(Concrete, reflector).fields_by_name['mode']

    assert get_member_value_structural_type_key(protocol_member, reflector) != concrete_member.structural_type_key


def test_inspect_protocol_members_replaces_parameterized_method_return() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class BoxLike(ta.Protocol[t_var]):  # type: ignore
        def get(self) -> t_var:  # type: ignore
            ...

    member = inspect_protocol_members(BoxLike[int]).members_by_name['get']  # type: ignore
    call_signature = get_member_call_signature(member)

    assert call_signature is not None
    assert type_str(call_signature.return_type) == 'builtins.int'
    assert inspect_protocol_members(BoxLike[int]).member_keys['get'] == get_protocol_member_key(member)  # type: ignore


def test_inspect_protocol_members_replaces_parameterized_data_member() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class HasValue(ta.Protocol[t_var]):  # type: ignore
        value: t_var  # type: ignore

    member = inspect_protocol_members(HasValue[int]).members_by_name['value']  # type: ignore
    value_type = get_member_value_type(member)

    assert value_type is not None
    assert type_str(value_type) == 'builtins.int'
    assert inspect_protocol_members(HasValue[int]).member_keys['value'] == get_protocol_member_key(  # type: ignore
        member,
    )


def test_inspect_protocol_members_includes_inherited_protocol_members() -> None:
    class HasName(ta.Protocol):
        name: str

    class Reader(HasName, ta.Protocol):
        def read(self) -> bytes:
            ...

    inspection = inspect_protocol_members(Reader)

    assert [*inspection.members_by_name] == ['read', 'name']
    assert type_str(get_member_value_type(inspection.members_by_name['name'])) == 'builtins.str'  # type: ignore
    read_signature = get_member_call_signature(inspection.members_by_name['read'])
    assert read_signature is not None
    assert type_str(read_signature.return_type) == 'builtins.bytes'


def test_inspect_protocol_members_rejects_non_protocol() -> None:
    class Concrete:
        pass

    with pytest.raises(ReflectionError, match='protocol source'):
        inspect_protocol_members(Concrete, RuntimeTypeReflector(RuntimeTypeUniverse()))


def test_protocol_member_key_fails_closed_for_unkeyable_member() -> None:
    member = RuntimeMember(
        'value',
        RuntimeMemberKind.DATA,
        object,
        inspect.Signature.empty,
        None,
        None,
        value_type=types.PartialType(None, None),
    )

    with pytest.raises(ReflectionError, match='not implemented'):
        get_protocol_member_key(member)
