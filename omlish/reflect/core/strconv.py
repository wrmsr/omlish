# ruff: noqa: SLF001
import io
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


class TypeStrVisitor(TypeVisitor[None]):
    def __init__(self, out: io.StringIO) -> None:
        super().__init__()

        self._out = out

    def visit_type_alias_type(self, typ: TypeAliasType) -> None:
        if typ._alias is None:
            self._out.write('<alias>')
        elif typ._args:
            self._out.write(typ._alias._fullname)
            self._out.write('[')
            self.write_list(typ._args)
            self._out.write(']')
        else:
            self._out.write(typ._alias._fullname)

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> None:
        typ._type_guard.accept(self)

    def visit_annotated_type(self, typ: AnnotatedType) -> None:
        self._out.write('Annotated[')
        typ._item.accept(self)
        self._out.write(', ...]')

    def visit_required_type(self, typ: RequiredType) -> None:
        if typ._required:
            self._out.write('Required[')
            typ._item.accept(self)
            self._out.write(']')
        else:
            self._out.write('NotRequired[')
            typ._item.accept(self)
            self._out.write(']')

    def visit_read_only_type(self, typ: ReadOnlyType) -> None:
        self._out.write('ReadOnly[')
        typ._item.accept(self)
        self._out.write(']')

    def visit_type_var(self, typ: TypeVarType) -> None:
        self._out.write(typ._name)

    def visit_param_spec(self, typ: ParamSpecType) -> None:
        self._out.write(typ._name)

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> None:
        self._out.write(typ._name)

    def visit_unbound_type(self, typ: UnboundType) -> None:
        if typ._args:
            self._out.write(typ._name)
            self._out.write('?[')
            self.write_list(typ._args)
            self._out.write(']')
        else:
            self._out.write(typ._name)
            self._out.write('?')

    def visit_callable_argument(self, typ: CallableArgument) -> None:
        if typ._name is None:
            typ._typ.accept(self)
        else:
            self._out.write(typ._name)
            self._out.write(': ')
            typ._typ.accept(self)

    def visit_type_list(self, typ: TypeList) -> None:
        self._out.write('<TypeList ')
        self.write_list(typ._items)
        self._out.write('>')

    def visit_unpack_type(self, typ: UnpackType) -> None:
        self._out.write('Unpack[')
        typ._type.accept(self)
        self._out.write(']')

    def visit_any(self, typ: AnyType) -> None:
        self._out.write('Any')

    def visit_uninhabited_type(self, typ: UninhabitedType) -> None:
        self._out.write('Never')

    def visit_none_type(self, typ: NoneType) -> None:
        self._out.write('None')

    def visit_erased_type(self, typ: ErasedType) -> None:
        self._out.write('<Erased>')

    def visit_deleted_type(self, typ: DeletedType) -> None:
        if typ._source is None:
            self._out.write('<Deleted>')
        else:
            self._out.write('<Deleted ')
            self._out.write(repr(typ._source))
            self._out.write('>')

    def visit_instance(self, typ: Instance) -> None:
        self._out.write(typ._type._fullname)
        if typ._args:
            self._out.write('[')
            self.write_list(typ._args)
            self._out.write(']')

    def visit_parameters(self, typ: Parameters) -> None:
        self._out.write('[')
        self.write_list(typ._arg_types)
        self._out.write(']')

    def visit_callable_type(self, typ: CallableType) -> None:
        if typ._is_ellipsis_args:
            self._out.write('def (...) -> ')
            typ._ret_type.accept(self)
        else:
            self._out.write('def (')
            self.write_list(typ._arg_types)
            self._out.write(') -> ')
            typ._ret_type.accept(self)

    def visit_overloaded(self, typ: Overloaded) -> None:
        self._out.write('Overload(')
        self.write_list(typ._items)
        self._out.write(')')

    def visit_tuple_type(self, typ: TupleType) -> None:
        if typ._items:
            self._out.write('tuple[')
            self.write_list(typ._items)
            self._out.write(']')
        else:
            self._out.write('tuple[()]')

    def visit_typeddict_type(self, typ: TypedDictType) -> None:
        self._out.write('TypedDict({')
        for i, (name, item_typ) in enumerate(typ._items.items()):
            if i:
                self._out.write(', ')
            self._out.write(repr(name))
            if name not in typ._required_keys:
                self._out.write('?')
            if name in typ._readonly_keys:
                self._out.write('=')
            self._out.write(': ')
            item_typ.accept(self)
        self._out.write('})')

    def visit_raw_expression_type(self, typ: RawExpressionType) -> None:
        self._out.write(repr(typ._literal_value))

    def visit_literal_type(self, typ: LiteralType) -> None:
        if typ._fallback._type._is_enum and isinstance(typ._value, str):
            self._out.write('Literal[')
            self._out.write(typ._fallback._type._fullname)
            self._out.write('.')
            self._out.write(str(typ._value))
            self._out.write(']')
        else:
            self._out.write('Literal[')
            self._out.write(repr(typ._value))
            self._out.write(']')

    def visit_union_type(self, typ: UnionType) -> None:
        self._out.write('Union[')
        self.write_list(typ._items)
        self._out.write(']')

    def visit_partial_type(self, typ: PartialType) -> None:
        if typ._type is None:
            self._out.write('<partial None>')
        else:
            self._out.write('<partial ')
            self._out.write(typ._type._fullname)
            self._out.write('>')

    def visit_ellipsis_type(self, typ: EllipsisType) -> None:
        self._out.write('...')

    def visit_type_type(self, typ: TypeType) -> None:
        self._out.write('type[')
        typ._item.accept(self)
        self._out.write(']')

    def visit_placeholder_type(self, typ: PlaceholderType) -> None:
        if typ._args:
            self._out.write('<placeholder ')
            self._out.write(typ._fullname)
            self._out.write('[')
            self.write_list(typ._args)
            self._out.write(']>')
        else:
            self._out.write('<placeholder ')
            self._out.write(typ._fullname)
            self._out.write('>')

    def write_list(self, typs: ta.Iterable[Type]) -> None:
        for i, typ in enumerate(typs):
            if i:
                self._out.write(', ')
            typ.accept(self)


def type_str(typ: Type) -> str:
    out = io.StringIO()
    typ.accept(TypeStrVisitor(out))
    return out.getvalue()


def type_info_str(info: TypeInfo) -> str:
    return info._fullname
