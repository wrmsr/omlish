from .. import symbols
from .. import types
from ..typetraverser import TypeTraverserVisitor
from ..typevisitor import BoolTypeQuery
from ..typevisitor import BoolTypeQueryMode


class RecordingTraverser(TypeTraverserVisitor):
    def __init__(self) -> None:
        super().__init__()

        self.seen: list[str] = []

    def visit_any(self, typ: types.AnyType) -> None:
        self.seen.append('AnyType')
        super().visit_any(typ)

    def visit_none_type(self, typ: types.NoneType) -> None:
        self.seen.append('NoneType')
        super().visit_none_type(typ)

    def visit_type_var(self, typ: types.TypeVarType) -> None:
        self.seen.append(f'TypeVarType:{typ.name}')
        super().visit_type_var(typ)

    def visit_instance(self, typ: types.Instance) -> None:
        self.seen.append(f'Instance:{typ.type.fullname}')
        super().visit_instance(typ)

    def visit_union_type(self, typ: types.UnionType) -> None:
        self.seen.append('UnionType')
        super().visit_union_type(typ)


class HasTypeVar(BoolTypeQuery):
    def __init__(self) -> None:
        super().__init__(BoolTypeQueryMode.ANY)

    def visit_type_var(self, typ: types.TypeVarType) -> bool:
        return True


def make_type_tree() -> types.UnionType:
    any_type = types.AnyType(types.TypeOfAny.EXPLICIT)
    type_var = types.TypeVarType(
        'T',
        'T',
        types.TypeVarId(1),
        [],
        any_type,
        any_type,
    )
    info = symbols.TypeInfo('Sequence', 'typing.Sequence')
    instance = types.Instance(info, [type_var])
    return types.UnionType([instance, types.NoneType()])


def test_type_traverser_walks_child_types() -> None:
    traverser = RecordingTraverser()

    make_type_tree().accept(traverser)

    assert traverser.seen == [
        'UnionType',
        'Instance:typing.Sequence',
        'TypeVarType:T',
        'AnyType',
        'NoneType',
    ]


def test_bool_type_query_combines_child_results() -> None:
    assert make_type_tree().accept(HasTypeVar())
    assert not types.NoneType().accept(HasTypeVar())
