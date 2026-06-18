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
    def visit_type_alias_type(self, typ: TypeAliasType) -> None:
        self.traverse_type_list(typ._args)

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> None:
        typ._type_guard.accept(self)

    def visit_annotated_type(self, typ: AnnotatedType) -> None:
        typ._item.accept(self)

    def visit_required_type(self, typ: RequiredType) -> None:
        typ._item.accept(self)

    def visit_read_only_type(self, typ: ReadOnlyType) -> None:
        typ._item.accept(self)

    def visit_type_var(self, typ: TypeVarType) -> None:
        typ._default.accept(self)

    def visit_param_spec(self, typ: ParamSpecType) -> None:
        typ._default.accept(self)

    def visit_type_var_tuple(self, typ: TypeVarTupleType) -> None:
        typ._default.accept(self)

    def visit_unbound_type(self, typ: UnboundType) -> None:
        self.traverse_type_list(typ._args)

    def visit_callable_argument(self, typ: CallableArgument) -> None:
        typ._typ.accept(self)

    def visit_type_list(self, typ: TypeList) -> None:
        self.traverse_type_list(typ._items)

    def visit_unpack_type(self, typ: UnpackType) -> None:
        typ._type.accept(self)

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
        self.traverse_type_list(typ._args)
        if typ._last_known_value is not None:
            typ._last_known_value.accept(self)

    def visit_parameters(self, typ: Parameters) -> None:
        self.traverse_type_list(typ._arg_types)

    def visit_callable_type(self, typ: CallableType) -> None:
        self.traverse_type_list(typ._arg_types)
        typ._ret_type.accept(self)
        typ._fallback.accept(self)

    def visit_overloaded(self, typ: Overloaded) -> None:
        self.traverse_type_list(typ._items)

    def visit_tuple_type(self, typ: TupleType) -> None:
        self.traverse_type_list(typ._items)
        typ._partial_fallback.accept(self)

    def visit_typeddict_type(self, typ: TypedDictType) -> None:
        self.traverse_types(typ._items.values())
        typ._fallback.accept(self)

    def visit_raw_expression_type(self, typ: RawExpressionType) -> None:
        pass

    def visit_literal_type(self, typ: LiteralType) -> None:
        typ._fallback.accept(self)

    def visit_union_type(self, typ: UnionType) -> None:
        self.traverse_type_list(typ._items)

    def visit_partial_type(self, typ: PartialType) -> None:
        if typ._value_type is not None:
            typ._value_type.accept(self)

    def visit_ellipsis_type(self, typ: EllipsisType) -> None:
        pass

    def visit_type_type(self, typ: TypeType) -> None:
        typ._item.accept(self)

    def visit_placeholder_type(self, typ: PlaceholderType) -> None:
        self.traverse_type_list(typ._args)

    def traverse_types(self, typs: ta.Iterable[Type]) -> None:
        for typ in typs:
            typ.accept(self)

    def traverse_type_list(self, typs: ta.Sequence[Type]) -> None:
        for typ in typs:
            typ.accept(self)
