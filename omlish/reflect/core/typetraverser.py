# ruff: noqa: SLF001
import typing as ta

from .typevisitor import TypeVisitor


if ta.TYPE_CHECKING:
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


try:
    from mypy_extensions import mypyc_attr
except ImportError:
    from ._mypycshim import mypyc_attr


##


@mypyc_attr(allow_interpreted_subclasses=True)
class TypeTraverserVisitor(TypeVisitor[None]):
    def traverse_type(self, typ: Type) -> None:
        # Allows overriding with enter/exit logic
        typ.accept(self)

    def traverse_types(self, typs: ta.Iterable[Type]) -> None:
        for typ in typs:
            self.traverse_type(typ)

    #

    def visit_type_alias_type(self, typ: TypeAliasType) -> None:
        self.traverse_types(typ._args)

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> None:
        self.traverse_type(typ._type_guard)

    def visit_annotated_type(self, typ: AnnotatedType) -> None:
        self.traverse_type(typ._item)

    def visit_required_type(self, typ: RequiredType) -> None:
        self.traverse_type(typ._item)

    def visit_read_only_type(self, typ: ReadOnlyType) -> None:
        self.traverse_type(typ._item)

    def visit_type_var(self, typ: TypeVarType) -> None:
        self.traverse_type(typ._default)

    def visit_param_spec(self, typ: ParamSpecType) -> None:
        self.traverse_type(typ._default)

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> None:
        self.traverse_type(typ._default)

    def visit_unbound_type(self, typ: UnboundType) -> None:
        self.traverse_types(typ._args)

    def visit_callable_argument(self, typ: CallableArgument) -> None:
        self.traverse_type(typ._typ)

    def visit_type_list(self, typ: TypeList) -> None:
        self.traverse_types(typ._items)

    def visit_unpack_type(self, typ: UnpackType) -> None:
        self.traverse_type(typ._type)

    def visit_any(self, typ: AnyType) -> None:
        pass

    def visit_uninhabited_type(self, typ: UninhabitedType) -> None:
        pass

    def visit_none_type(self, typ: NoneType) -> None:
        pass

    def visit_erased_type(self, typ: ErasedType) -> None:
        pass

    def visit_deleted_type(self, typ: DeletedType) -> None:
        pass

    def visit_instance(self, typ: Instance) -> None:
        self.traverse_types(typ._args)
        if typ._last_known_value is not None:
            self.traverse_type(typ._last_known_value)

    def visit_parameters(self, typ: Parameters) -> None:
        self.traverse_types(typ._arg_types)

    def visit_callable_type(self, typ: CallableType) -> None:
        self.traverse_types(typ._arg_types)
        self.traverse_type(typ._ret_type)
        self.traverse_type(typ._fallback)

    def visit_overloaded(self, typ: Overloaded) -> None:
        self.traverse_types(typ._items)

    def visit_tuple_type(self, typ: TupleType) -> None:
        self.traverse_types(typ._items)
        self.traverse_type(typ._partial_fallback)

    def visit_typeddict_type(self, typ: TypedDictType) -> None:
        self.traverse_types(typ._items.values())
        self.traverse_type(typ._fallback)

    def visit_raw_expression_type(self, typ: RawExpressionType) -> None:
        pass

    def visit_literal_type(self, typ: LiteralType) -> None:
        self.traverse_type(typ._fallback)

    def visit_union_type(self, typ: UnionType) -> None:
        self.traverse_types(typ._items)

    def visit_partial_type(self, typ: PartialType) -> None:
        if typ._value_type is not None:
            self.traverse_type(typ._value_type)

    def visit_ellipsis_type(self, typ: EllipsisType) -> None:
        pass

    def visit_type_type(self, typ: TypeType) -> None:
        self.traverse_type(typ._item)

    def visit_placeholder_type(self, typ: PlaceholderType) -> None:
        self.traverse_types(typ._args)
