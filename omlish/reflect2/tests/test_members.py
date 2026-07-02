# ruff: noqa: F821 PLC0132 SLF001
import inspect
import threading
import typing as ta

from ..core import types
from ..core.strconv import type_str
from ..errors import ReflectionError
from ..interning import Interner
from ..members import MemberKind
from ..members import MembersInspector
from ..reflector import TypeReflector
from ..typekeys import TypeKeys
from ..universe import TypeUniverse


def make_members_inspector() -> MembersInspector:
    return MembersInspector(
        keys=TypeKeys(
            lock=(lock := threading.RLock()),
        ),
        reflector=TypeReflector(
            universe=TypeUniverse(
                lock=lock,
            ),
            interner=Interner(
                lock=lock,
            ),
            lock=lock,
        ),
        lock=lock,
    )


def test_inspect_runtime_members_classifies_descriptor_kinds() -> None:
    class Example:
        data = 1

        def method(self, value: int) -> str:
            return str(value)

        @staticmethod
        def static(value: int) -> str:
            return str(value)

        @classmethod
        def class_method(cls, value: int) -> str:
            return str(value)

        @property
        def prop(self) -> int:
            return 1

    mr = make_members_inspector()
    inspection = mr.inspect_members(Example)

    assert inspection.origin is Example
    assert inspection.members_by_name['data'].kind == MemberKind.DATA
    assert inspection.members_by_name['method'].kind == MemberKind.FUNCTION
    assert inspection.members_by_name['static'].kind == MemberKind.STATICMETHOD
    assert inspection.members_by_name['class_method'].kind == MemberKind.CLASSMETHOD
    assert inspection.members_by_name['prop'].kind == MemberKind.PROPERTY


def test_inspect_runtime_members_exposes_unbound_signatures() -> None:
    class Example:
        def method(self, value: int) -> str:
            return str(value)

        @staticmethod
        def static(value: int) -> str:
            return str(value)

        @classmethod
        def class_method(cls, value: int) -> str:
            return str(value)

    mr = make_members_inspector()
    members = mr.inspect_members(Example).members_by_name

    assert tuple(members['method'].signature.parameters) == ('self', 'value')  # type: ignore
    assert members['method'].signature.return_annotation is str  # type: ignore
    assert tuple(members['static'].signature.parameters) == ('value',)  # type: ignore
    assert tuple(members['class_method'].signature.parameters) == ('cls', 'value')  # type: ignore


def test_inspect_runtime_members_reflects_method_signatures() -> None:
    class Example:
        def method(self, value: int) -> str:
            return str(value)

        @staticmethod
        def static(value: int) -> str:
            return str(value)

        @classmethod
        def class_method(cls, value: int) -> str:
            return str(value)

    mr = make_members_inspector()
    members = mr.inspect_members(Example).members_by_name

    method_sig = members['method'].reflected_signature
    assert method_sig is not None
    assert [parameter.name for parameter in method_sig.parameters] == ['self', 'value']
    assert isinstance(method_sig.parameters[0].typ, types.AnyType)
    assert type_str(method_sig.parameters[1].typ) == 'builtins.int'
    assert type_str(method_sig.return_type) == 'builtins.str'

    static_sig = members['static'].reflected_signature
    assert static_sig is not None
    assert [parameter.name for parameter in static_sig.parameters] == ['value']
    assert type_str(static_sig.parameters[0].typ) == 'builtins.int'

    class_sig = members['class_method'].reflected_signature
    assert class_sig is not None
    assert [parameter.name for parameter in class_sig.parameters] == ['cls', 'value']
    assert isinstance(class_sig.parameters[0].typ, types.AnyType)
    assert type_str(class_sig.parameters[1].typ) == 'builtins.int'


def test_inspect_runtime_members_preserves_literal_newtype_method_signature_shape() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    class Example:
        def set_mode(self, mode: mode) -> mode:
            return mode

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['set_mode']
    signature = member.reflected_signature
    call_signature = member.get_call_signature()

    assert signature is not None
    assert call_signature is not None
    assert [parameter.name for parameter in signature.parameters] == ['self', 'mode']
    # assert reflector.to_runtime_annotation(signature.parameters[1].typ) is mode
    # assert reflector.to_runtime_annotation(signature.return_type) is mode
    # parameter_shape = get_runtime_type_shape(call_signature.parameters[0].typ, reflector)
    # return_shape = get_runtime_type_shape(call_signature.return_type, reflector)
    # assert parameter_shape.new_type is not None
    # assert parameter_shape.new_type.obj is mode
    # assert parameter_shape.literal_value_type is not None
    # assert parameter_shape.literal_value_type.values == ('a', 'b')
    # assert return_shape.new_type is not None
    # assert return_shape.new_type.obj is mode
    # assert return_shape.literal_value_type is not None
    # assert return_shape.literal_value_type.values == ('a', 'b')


def test_inspect_runtime_members_preserves_parameter_kinds_and_defaults() -> None:
    class Example:
        def method(self, value: int, /, named: str, *, flag: bool = False) -> None:
            raise NotImplementedError

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['method']
    signature = member.reflected_signature

    assert signature is not None
    assert [
        (parameter.name, parameter.kind, type_str(parameter.typ), parameter.has_default)
        for parameter in signature.parameters
    ] == [
        ('self', inspect.Parameter.POSITIONAL_ONLY, 'Any', False),
        ('value', inspect.Parameter.POSITIONAL_ONLY, 'builtins.int', False),
        ('named', inspect.Parameter.POSITIONAL_OR_KEYWORD, 'builtins.str', False),
        ('flag', inspect.Parameter.KEYWORD_ONLY, 'builtins.bool', True),
    ]
    assert type_str(signature.return_type) == 'None'


# def test_member_signature_key_includes_parameter_kind_and_default_presence() -> None:
#     class Left:
#         def method(self, value: int, *, flag: bool = False) -> None:
#             raise NotImplementedError
#
#     class DifferentKind:
#         def method(self, value: int, flag: bool = False) -> None:
#             raise NotImplementedError
#
#     class DifferentDefault:
#         def method(self, value: int, *, flag: bool) -> None:
#             raise NotImplementedError
#
#     mr = make_members_reflector()
#     left_key = mr.get_member_call_signature_key(mr.inspect_runtime_members(Left).members_by_name['method'])
#     different_kind_key = mr.get_member_call_signature_key(
#         mr.inspect_runtime_members(DifferentKind).members_by_name['method'],
#     )
#     different_default_key = mr.get_member_call_signature_key(
#         mr.inspect_runtime_members(DifferentDefault).members_by_name['method'],
#     )
#
#     assert left_key != different_kind_key
#     assert left_key != different_default_key


def test_inspect_runtime_members_reflects_property_getter_return_type() -> None:
    class Example:
        @property
        def value(self) -> int:
            return 1

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['value']

    assert member.kind == MemberKind.PROPERTY
    assert member.reflected_signature is not None
    assert [parameter.name for parameter in member.reflected_signature.parameters] == ['self']
    assert type_str(member.reflected_signature.return_type) == 'builtins.int'


def test_inspect_runtime_members_uses_any_for_omitted_annotations() -> None:
    class Example:
        def method(self, value):
            return value

    mr = make_members_inspector()
    reflected_signature = mr.inspect_members(Example).members_by_name['method'].reflected_signature

    assert reflected_signature is not None
    assert all(isinstance(parameter.typ, types.AnyType) for parameter in reflected_signature.parameters)
    assert isinstance(reflected_signature.return_type, types.AnyType)


def test_get_member_call_signature_drops_self_for_instance_method() -> None:
    class Example:
        def method(self, value: int) -> str:
            return str(value)

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['method']
    call_signature = member.get_call_signature()

    assert call_signature is not None
    assert [parameter.name for parameter in call_signature.parameters] == ['value']
    assert type_str(call_signature.parameters[0].typ) == 'builtins.int'
    assert type_str(call_signature.return_type) == 'builtins.str'


def test_get_member_call_signature_drops_cls_for_classmethod() -> None:
    class Example:
        @classmethod
        def create(cls, value: int) -> str:
            return str(value)

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['create']
    call_signature = member.get_call_signature()

    assert call_signature is not None
    assert [parameter.name for parameter in call_signature.parameters] == ['value']
    assert type_str(call_signature.parameters[0].typ) == 'builtins.int'


def test_get_member_call_signature_keeps_staticmethod_parameters() -> None:
    class Example:
        @staticmethod
        def create(value: int) -> str:
            return str(value)

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['create']
    call_signature = member.get_call_signature()

    assert call_signature is not None
    assert [parameter.name for parameter in call_signature.parameters] == ['value']
    assert type_str(call_signature.parameters[0].typ) == 'builtins.int'


def test_get_member_value_type_exposes_property_return_type() -> None:
    class Example:
        @property
        def value(self) -> int:
            return 1

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['value']
    value_type = member.get_value_type()

    assert value_type is not None
    assert type_str(value_type) == 'builtins.int'
    assert member.get_call_signature() is None


# def test_member_signature_key_matches_equivalent_call_signatures() -> None:
#     class Left:
#         def method(self, value: int) -> str:
#             return str(value)
#
#     class Right:
#         def method(self, value: int) -> str:
#             return str(value)
#
#     mr = make_members_reflector()
#     left = mr.inspect_runtime_members(Left).members_by_name['method']
#     right = mr.inspect_runtime_members(Right).members_by_name['method']
#
#     assert mr.get_member_call_signature_key(left) == mr.get_member_call_signature_key(right)


# def test_member_signature_key_changes_for_different_return_type() -> None:
#     class Left:
#         def method(self, value: int) -> str:
#             return str(value)
#
#     class Right:
#         def method(self, value: int) -> int:
#             return value
#
#     mr = make_members_reflector()
#     left = mr.inspect_runtime_members(Left).members_by_name['method']
#     right = mr.inspect_runtime_members(Right).members_by_name['method']
#
#     assert mr.get_member_call_signature_key(left) != mr.get_member_call_signature_key(right)


# def test_member_signature_key_changes_for_different_parameter_type() -> None:
#     class Left:
#         def method(self, value: int) -> str:
#             return str(value)
#
#     class Right:
#         def method(self, value: str) -> str:
#             return value
#
#     mr = make_members_reflector()
#     left = mr.inspect_runtime_members(Left).members_by_name['method']
#     right = mr.inspect_runtime_members(Right).members_by_name['method']
#
#     assert mr.get_member_call_signature_key(left) != mr.get_member_call_signature_key(right)


# def test_member_call_signature_key_matches_instance_method_and_staticmethod_public_shape() -> None:
#     class Left:
#         def method(self, value: int) -> str:
#             return str(value)
#
#     class Right:
#         @staticmethod
#         def method(value: int) -> str:
#             return str(value)
#
#     mr = make_members_reflector()
#     left = mr.inspect_runtime_members(Left).members_by_name['method']
#     right = mr.inspect_runtime_members(Right).members_by_name['method']
#
#     assert mr.get_member_call_signature_key(left) == mr.get_member_call_signature_key(right)


# def test_member_value_type_key_matches_property_type_key() -> None:
#     class Example:
#         @property
#         def value(self) -> int:
#             return 1
#
#     mr = make_members_reflector()
#     member = mr.inspect_runtime_members(Example).members_by_name['value']
#
#     assert mr.get_member_value_type_key(member) == type_key(types.Instance(TypeUniverse().get_type_info(int), []))


# def test_member_signature_key_fails_closed_for_unkeyable_type() -> None:
#     call_signature = RuntimeMemberSignature(
#         (
#             RuntimeMemberParameter(
#                 'value',
#                 inspect.Parameter.POSITIONAL_OR_KEYWORD,
#                 types.PartialType(None, None),
#                 False,
#             ),
#         ),
#         types.Instance(TypeUniverse().get_type_info(int), []),
#     )
#
#     mr = make_members_reflector()
#     try:
#         mr.member_signature_key(call_signature)
#     except ReflectionError as e:
#         assert 'not implemented' in str(e)  # noqa
#     else:
#         raise AssertionError('expected TypeError')


def test_callable_data_member_has_no_member_call_signature() -> None:
    class CallableValue:
        def __call__(self, value: int) -> str:
            return str(value)

    class Example:
        callback = staticmethod(lambda value: value)
        callable_value = CallableValue()

    mr = make_members_inspector()
    members = mr.inspect_members(Example).members_by_name

    assert members['callback'].kind == MemberKind.STATICMETHOD
    assert members['callback'].get_call_signature() is not None
    assert members['callable_value'].kind == MemberKind.DATA
    assert members['callable_value'].get_call_signature() is None


def test_inspect_runtime_members_uses_subclass_owner_for_overrides() -> None:
    class Base:
        def method(self) -> int:
            return 1

    class Child(Base):
        def method(self) -> str:  # type: ignore
            return 'x'

    mr = make_members_inspector()
    member = mr.inspect_members(Child).members_by_name['method']

    assert member.owner is Child
    assert member.kind == MemberKind.FUNCTION
    assert member.signature.return_annotation is str  # type: ignore


# def test_dataclass_instance_field_is_record_field_not_class_member() -> None:
#     @dc.dataclass
#     class Example:
#         value: int
#
#         def method(self) -> int:
#             return self.value
#
#     reflector = TypeReflector(TypeUniverse())
#     record = inspect_record(Example, reflector)
#     members = inspect_runtime_members(Example)
#
#     assert [field.name for field in record.fields] == ['value']
#     assert 'value' not in members.members_by_name
#     assert members.members_by_name['method'].kind == RuntimeMemberKind.FUNCTION


# def test_dataclass_field_with_default_is_class_data_member_and_record_field() -> None:
#     @dc.dataclass
#     class Example:
#         value: int = 1
#
#     reflector = TypeReflector(TypeUniverse())
#     record = inspect_record(Example, reflector)
#     members = inspect_runtime_members(Example)
#
#     assert [field.name for field in record.fields] == ['value']
#     assert members.members_by_name['value'].kind == RuntimeMemberKind.DATA


def test_inspect_runtime_members_accepts_parameterized_alias_origin() -> None:
    class Box[T]:
        def get(self) -> T:
            raise NotImplementedError

    mr = make_members_inspector()
    inspection = mr.inspect_members(Box[int])

    assert inspection.origin is Box
    assert inspection.members_by_name['get'].kind == MemberKind.FUNCTION


def test_inspect_runtime_members_replaces_parameterized_alias_method_return() -> None:
    class Box[T]:
        def get(self) -> T:
            raise NotImplementedError

    mr = make_members_inspector()
    member = mr.inspect_members(Box[int]).members_by_name['get']
    call_signature = member.get_call_signature()

    assert call_signature is not None
    assert type_str(call_signature.return_type) == 'builtins.int'


def test_inspect_runtime_members_replaces_parameterized_alias_method_parameter() -> None:
    class Box[T]:
        def put(self, value: T) -> None:
            raise NotImplementedError

    mr = make_members_inspector()
    member = mr.inspect_members(Box[int]).members_by_name['put']
    call_signature = member.get_call_signature()

    assert call_signature is not None
    assert [parameter.name for parameter in call_signature.parameters] == ['value']
    assert type_str(call_signature.parameters[0].typ) == 'builtins.int'
    assert type_str(call_signature.return_type) == 'None'


def test_inspect_runtime_members_uses_any_for_unparameterized_generic_method() -> None:
    class Box[T]:
        def get(self) -> T:
            raise NotImplementedError

    mr = make_members_inspector()
    member = mr.inspect_members(Box).members_by_name['get']
    call_signature = member.get_call_signature()

    assert call_signature is not None
    assert isinstance(call_signature.return_type, types.AnyType)


def test_inspect_runtime_members_replaces_inherited_generic_method() -> None:
    class Box[T]:
        def get(self) -> T:
            raise NotImplementedError

    class StrBox(Box[str]):
        pass

    mr = make_members_inspector()
    member = mr.inspect_members(StrBox).members_by_name['get']
    call_signature = member.get_call_signature()

    assert member.owner is Box
    assert call_signature is not None
    assert type_str(call_signature.return_type) == 'builtins.str'


def test_inspect_runtime_members_replaces_inherited_generic_method_with_literal_newtype() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    class Box[T]:
        def get(self) -> T:
            raise NotImplementedError

        def put(self, value: T) -> T:
            raise NotImplementedError

    class ModeBox(Box[mode]):  # noqa
        pass

    mr = make_members_inspector()
    members = mr.inspect_members(ModeBox).members_by_name
    get_signature = members['get'].get_call_signature()
    put_signature = members['put'].get_call_signature()

    assert get_signature is not None
    assert put_signature is not None
    # assert reflector.to_runtime_annotation(get_signature.return_type) is mode
    # assert reflector.to_runtime_annotation(put_signature.parameters[0].typ) is mode
    # assert reflector.to_runtime_annotation(put_signature.return_type) is mode
    # get_shape = get_runtime_type_shape(get_signature.return_type, reflector)
    # put_shape = get_runtime_type_shape(put_signature.parameters[0].typ, reflector)
    # assert get_shape.new_type is not None
    # assert get_shape.new_type.obj is mode
    # assert get_shape.literal_value_type is not None
    # assert get_shape.literal_value_type.values == ('a', 'b')
    # assert put_shape.new_type is not None
    # assert put_shape.new_type.obj is mode
    # assert put_shape.literal_value_type is not None
    # assert put_shape.literal_value_type.values == ('a', 'b')


# def test_inspect_runtime_members_expands_new_type_literal_alias_collection_signature() -> None:
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#     mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore
#
#     class Service:
#         def set_modes(self, modes: mode_list) -> mode_list:  # type: ignore
#             return modes
#
#     mr = make_members_reflector()
#     member = mr.inspect_runtime_members(Service).members_by_name['set_modes']
#     signature = member.get_call_signature()
#
#     assert signature is not None
#     assert reflector.to_runtime_annotation(signature.parameters[0].typ) == list[mode]  # noqa
#     assert reflector.to_runtime_annotation(signature.return_type) == list[mode]  # noqa
#     parameter_shape = get_runtime_collection_shape(signature.parameters[0].typ)
#     return_shape = get_runtime_collection_shape(signature.return_type)
#     assert parameter_shape.sequence_item is not None
#     assert return_shape.sequence_item is not None
#     parameter_item = get_runtime_type_shape(parameter_shape.sequence_item)
#     return_item = get_runtime_type_shape(return_shape.sequence_item)
#     assert parameter_item.new_type is not None
#     assert parameter_item.new_type.obj is mode
#     assert parameter_item.literal_value_type is not None
#     assert parameter_item.literal_value_type.values == ('a', 'b')
#     assert return_item.new_type is not None
#     assert return_item.new_type.obj is mode
#     assert return_item.literal_value_type is not None
#     assert return_item.literal_value_type.values == ('a', 'b')
#     assert type_key(signature.return_type) != type_key(mr._reflector.reflect_type(list[ta.Literal['a', 'b']]))


def test_member_alias_signature_keeps_nominal_key_but_matches_effective_key() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    class Left:
        def set_modes(self, modes: mode_list) -> mode_list:  # type: ignore
            return modes

    class Right:
        def set_modes(self, modes: list[mode]) -> list[mode]:  # noqa
            return modes

    mr = make_members_inspector()
    left_member = mr.inspect_members(Left).members_by_name['set_modes']
    right_member = mr.inspect_members(Right).members_by_name['set_modes']
    left_signature = left_member.get_call_signature()
    right_signature = right_member.get_call_signature()

    assert left_signature is not None
    assert right_signature is not None
    # assert reflector.to_runtime_annotation(
    #     left_signature.return_type,
    #     type_alias_policy='preserve',
    # ) is mode_list
    # assert is_structurally_equivalent(left_signature.return_type, right_signature.return_type)
    # assert get_member_call_signature_key(left_member) != get_member_call_signature_key(right_member)
    # assert get_member_call_signature_key(left_member, reflector) == get_member_call_signature_key(
    #     right_member,
    #     reflector,
    # )
    # assert get_member_call_structural_signature_key(left_member, reflector) == \
    #        get_member_call_structural_signature_key(right_member, reflector)


# def test_member_structural_signature_key_preserves_new_type_identity() -> None:
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#     other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore
#
#     class Left:
#         def set_mode(self, mode: mode) -> mode:
#             return mode
#
#     class Right:
#         def set_mode(self, mode: other_mode) -> other_mode:
#             return mode
#
#     reflector = TypeReflector(TypeUniverse())
#     left_member = inspect_runtime_members(Left, reflector).members_by_name['set_mode']
#     right_member = inspect_runtime_members(Right, reflector).members_by_name['set_mode']
#
#     assert get_member_call_structural_signature_key(left_member, reflector) != \
#         get_member_call_structural_signature_key(right_member, reflector, )


# def test_member_recursive_alias_signature_structural_key_matches_unrolled_type() -> None:
#     alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
#
#     class Service:
#         def visit(self, node: alias) -> tuple[alias]:  # type: ignore
#             raise NotImplementedError
#
#     reflector = TypeReflector(
#         TypeUniverse(),
#         forward_ref_resolver={'Node': alias}.__getitem__,
#     )
#     member = inspect_runtime_members(Service, reflector).members_by_name['visit']
#     signature = get_member_call_signature(member)
#
#     assert signature is not None
#     [parameter] = signature.parameters
#     assert structural_type_key(parameter.typ) == structural_type_key(
#         reflector.reflect_type(int | list[alias]),  # type: ignore
#     )
#     assert structural_type_key(signature.return_type) == structural_type_key(
#         reflector.reflect_type(tuple[int | list[alias]]),  # type: ignore
#     )
#     assert get_member_call_structural_signature_key(member, reflector) == (
#         'member_signature',
#         (
#             (
#                 'node',
#                 inspect.Parameter.POSITIONAL_OR_KEYWORD,
#                 reflector.structural_type_key(reflector.reflect_type(int | list[alias])),  # type: ignore
#                 False,
#             ),
#         ),
#         reflector.structural_type_key(reflector.reflect_type(tuple[int | list[alias]])),  # type: ignore
#     )


# def test_member_value_structural_type_key_matches_alias_expanded_property() -> None:
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#     mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore
#
#     class Left:
#         @property
#         def modes(self) -> mode_list:  # type: ignore
#             raise NotImplementedError
#
#     class Right:
#         @property
#         def modes(self) -> list[mode]:  # noqa
#             raise NotImplementedError
#
#     reflector = TypeReflector(TypeUniverse())
#     left_member = inspect_runtime_members(Left, reflector).members_by_name['modes']
#     right_member = inspect_runtime_members(Right, reflector).members_by_name['modes']
#
#     assert get_member_value_type_key(left_member) != get_member_value_type_key(right_member)
#     assert get_member_value_structural_type_key(left_member, reflector) == get_member_value_structural_type_key(
#         right_member,
#         reflector,
#     )


# def test_inspect_runtime_members_expands_generic_new_type_literal_alias_collection_signature() -> None:
#     t_var = ta.TypeVar('T')  # type: ignore
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#     other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore
#     box_alias = ta.TypeAliasType('BoxAlias', list[t_var], type_params=(t_var,))  # type: ignore
#
#     class Service:
#         def set_modes(self, modes: box_alias[mode]) -> box_alias[mode]:  # type: ignore
#             return modes
#
#     mr = make_members_reflector()
#     member = mr.inspect_runtime_members(Service).members_by_name['set_modes']
#     signature = member.get_call_signature()
#
#     assert signature is not None
#     assert mr._reflector.to_runtime_annotation(signature.parameters[0].typ) == list[mode]  # noqa
#     assert mr._reflector.to_runtime_annotation(signature.return_type) == list[mode]  # noqa
#     collection_shape = get_runtime_collection_shape(signature.parameters[0].typ, reflector)
#     assert collection_shape.sequence_item is not None
#     item_shape = get_runtime_type_shape(collection_shape.sequence_item, reflector)
#     assert item_shape.new_type is not None
#     assert item_shape.new_type.obj is mode
#     assert item_shape.literal_value_type is not None
#     assert item_shape.literal_value_type.values == ('a', 'b')
#     assert type_key(signature.return_type) != type_key(reflector.reflect_type(box_alias[other_mode]))
#     assert type_key(signature.return_type) != type_key(
#         reflector.reflect_type(box_alias[ta.Literal['a', 'b']]),
#     )


# def test_inspect_runtime_members_marks_unreflectable_alias_signature_unkeyable() -> None:
#     bad_alias = ta.TypeAliasType('BadAlias', ta.TypeIs[int])  # type: ignore
#
#     class Service:
#         def check(self, value: bad_alias) -> bool:  # type: ignore
#             return bool(value)
#
#     reflector = TypeReflector(TypeUniverse())
#     member = inspect_runtime_members(Service, reflector).members_by_name['check']
#
#     assert member.unkeyable
#     assert member.reflected_signature is None
#     assert get_member_call_signature(member) is None
#     with pytest.raises(ReflectionError, match='not keyable'):
#         get_member_call_signature_key(member)


def test_inspect_runtime_members_rejects_non_type_source() -> None:
    mr = make_members_inspector()
    try:
        mr.inspect_members(1)
    except ReflectionError as e:
        assert 'member source' in str(e)  # noqa
    else:
        raise AssertionError('expected TypeError')


def test_member_order_is_base_then_subclass_with_overrides_in_place() -> None:
    class Base:
        base_data = 1

        def method(self) -> int:
            return 1

    class Child(Base):
        child_data = 2

        def method(self) -> str:  # type: ignore
            return 'x'

    mr = make_members_inspector()
    inspection = mr.inspect_members(Child)

    assert [member.name for member in inspection.members] == ['base_data', 'method', 'child_data']
    assert inspection.members_by_name['method'].owner is Child
    assert isinstance(inspection.members_by_name['method'].signature, inspect.Signature)


def test_inspect_runtime_members_collects_typing_overloads() -> None:
    class Example:
        @ta.overload
        def method(self, value: int) -> int:
            ...

        @ta.overload
        def method(self, value: str) -> str:
            ...

        def method(self, value):
            return value

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['method']
    signatures = member.get_call_signatures()

    assert len(signatures) == 2
    assert [type_str(signature.parameters[0].typ) for signature in signatures] == [
        'builtins.int',
        'builtins.str',
    ]
    assert [type_str(signature.return_type) for signature in signatures] == [
        'builtins.int',
        'builtins.str',
    ]


def test_inspect_runtime_members_collects_overload_keyword_only_defaults() -> None:
    class Example:
        @ta.overload
        def method(self, value: int, *, flag: bool = False) -> int:
            ...

        @ta.overload
        def method(self, value: str, *, flag: bool) -> str:
            ...

        def method(self, value, *, flag=False):
            return value

    mr = make_members_inspector()
    member = mr.inspect_members(Example).members_by_name['method']
    signatures = member.get_call_signatures()

    assert len(signatures) == 2
    assert [
        [
            (parameter.name, parameter.kind, type_str(parameter.typ), parameter.has_default)
            for parameter in signature.parameters
        ]
        for signature in signatures
    ] == [
        [
            ('value', inspect.Parameter.POSITIONAL_OR_KEYWORD, 'builtins.int', False),
            ('flag', inspect.Parameter.KEYWORD_ONLY, 'builtins.bool', True),
        ],
        [
            ('value', inspect.Parameter.POSITIONAL_OR_KEYWORD, 'builtins.str', False),
            ('flag', inspect.Parameter.KEYWORD_ONLY, 'builtins.bool', False),
        ],
    ]
    assert [type_str(signature.return_type) for signature in signatures] == [
        'builtins.int',
        'builtins.str',
    ]


# def test_overloaded_member_call_signature_keys_preserve_overload_order() -> None:
#     class Left:
#         @ta.overload
#         def method(self, value: int) -> int:
#             ...
#
#         @ta.overload
#         def method(self, value: str) -> str:
#             ...
#
#         def method(self, value):
#             return value
#
#     class Right:
#         @ta.overload
#         def method(self, value: str) -> str:
#             ...
#
#         @ta.overload
#         def method(self, value: int) -> int:
#             ...
#
#         def method(self, value):
#             return value
#
#     mr = make_members_reflector()
#     left_signatures = mr.inspect_runtime_members(Left).members_by_name['method'].get_call_signatures()  # noqa
#     right_signatures = mr.inspect_runtime_members(Right).members_by_name['method'].get_call_signatures()  # noqa
#
#     assert [mr.member_signature_key(signature) for signature in left_signatures] != [
#         mr.member_signature_key(signature)
#         for signature in right_signatures
#     ]
