# ruff: noqa: SLF001
import typing as ta

from .symbols import TypeInfo
from .types import AnnotatedType
from .types import AnyType
from .types import CallableArgument
from .types import CallableType
from .types import DeletedType
from .types import EllipsisType
from .types import ErasedType
from .types import Instance
from .types import LiteralType
from .types import NoneType
from .types import Overloaded
from .types import Parameters
from .types import ParamSpecType
from .types import PartialType
from .types import PlaceholderType
from .types import RawExpressionType
from .types import ReadOnlyType
from .types import RequiredType
from .types import TupleType
from .types import Type
from .types import TypeAliasType
from .types import TypedDictType
from .types import TypeGuardedType
from .types import TypeList
from .types import TypeType
from .types import TypeVarTupleType
from .types import TypeVarType
from .types import UnboundType
from .types import UninhabitedType
from .types import UnionType
from .types import UnpackType
from .typevisitor import TypeVisitor


##


class TypeStrVisitor(TypeVisitor[str]):
    def visit_type_alias_type(self, typ: TypeAliasType) -> str:
        if typ._alias is None:
            return '<alias>'
        if typ._args:
            return f'{typ._alias._fullname}[{self.list_str(typ._args)}]'
        return typ._alias._fullname

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> str:
        return typ._type_guard.accept(self)

    def visit_annotated_type(self, typ: AnnotatedType) -> str:
        return f'Annotated[{typ._item.accept(self)}, ...]'

    def visit_required_type(self, typ: RequiredType) -> str:
        if typ._required:
            return f'Required[{typ._item.accept(self)}]'
        return f'NotRequired[{typ._item.accept(self)}]'

    def visit_read_only_type(self, typ: ReadOnlyType) -> str:
        return f'ReadOnly[{typ._item.accept(self)}]'

    def visit_type_var(self, typ: TypeVarType) -> str:
        return typ._name

    def visit_param_spec(self, typ: ParamSpecType) -> str:
        return typ._name

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> str:
        return typ._name

    def visit_unbound_type(self, typ: UnboundType) -> str:
        if typ._args:
            return f'{typ._name}?[{self.list_str(typ._args)}]'
        return f'{typ._name}?'

    def visit_callable_argument(self, typ: CallableArgument) -> str:
        if typ._name is None:
            return typ._typ.accept(self)
        return f'{typ._name}: {typ._typ.accept(self)}'

    def visit_type_list(self, typ: TypeList) -> str:
        return f'<TypeList {self.list_str(typ._items)}>'

    def visit_unpack_type(self, typ: UnpackType) -> str:
        return f'Unpack[{typ._type.accept(self)}]'

    def visit_any(self, typ: AnyType) -> str:
        return 'Any'

    def visit_uninhabited_type(self, typ: UninhabitedType) -> str:
        return 'Never'

    def visit_none_type(self, typ: NoneType) -> str:
        return 'None'

    def visit_erased_type(self, typ: ErasedType) -> str:
        return '<Erased>'

    def visit_deleted_type(self, typ: DeletedType) -> str:
        if typ._source is None:
            return '<Deleted>'
        return f'<Deleted {typ._source!r}>'

    def visit_instance(self, typ: Instance) -> str:
        ret = typ._type._fullname
        if typ._args:
            ret += f'[{self.list_str(typ._args)}]'
        return ret

    def visit_parameters(self, typ: Parameters) -> str:
        return f'[{self.list_str(typ._arg_types)}]'

    def visit_callable_type(self, typ: CallableType) -> str:
        if typ._is_ellipsis_args:
            return f'def (...) -> {typ._ret_type.accept(self)}'
        return f'def ({self.list_str(typ._arg_types)}) -> {typ._ret_type.accept(self)}'

    def visit_overloaded(self, typ: Overloaded) -> str:
        return f'Overload({self.list_str(typ._items)})'

    def visit_tuple_type(self, typ: TupleType) -> str:
        if typ._items:
            return f'tuple[{self.list_str(typ._items)}]'
        return 'tuple[()]'

    def visit_typeddict_type(self, typ: TypedDictType) -> str:
        item_strs: list[str] = []
        for name, item_typ in typ._items.items():
            suffix = ''
            if name not in typ._required_keys:
                suffix += '?'
            if name in typ._readonly_keys:
                suffix += '='
            item_strs.append(f'{name!r}{suffix}: {item_typ.accept(self)}')
        return f'TypedDict({{{", ".join(item_strs)}}})'

    def visit_raw_expression_type(self, typ: RawExpressionType) -> str:
        return repr(typ._literal_value)

    def visit_literal_type(self, typ: LiteralType) -> str:
        if typ._fallback._type._is_enum and isinstance(typ._value, str):
            return f'Literal[{typ._fallback._type._fullname}.{typ._value}]'
        return f'Literal[{typ._value!r}]'

    def visit_union_type(self, typ: UnionType) -> str:
        return f'Union[{self.list_str(typ._items)}]'

    def visit_partial_type(self, typ: PartialType) -> str:
        if typ._type is None:
            return '<partial None>'
        return f'<partial {typ._type._fullname}>'

    def visit_ellipsis_type(self, typ: EllipsisType) -> str:
        return '...'

    def visit_type_type(self, typ: TypeType) -> str:
        return f'type[{typ._item.accept(self)}]'

    def visit_placeholder_type(self, typ: PlaceholderType) -> str:
        if typ._args:
            return f'<placeholder {typ._fullname}[{self.list_str(typ._args)}]>'
        return f'<placeholder {typ._fullname}>'

    def list_str(self, typs: ta.Iterable[Type]) -> str:
        return ', '.join(typ.accept(self) for typ in typs)


def type_str(typ: Type) -> str:
    return typ.accept(TypeStrVisitor())


def type_info_str(info: TypeInfo) -> str:
    return info._fullname
