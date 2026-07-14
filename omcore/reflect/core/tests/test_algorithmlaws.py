# ruff: noqa: SLF001
from ..constraints import Constraint
from ..constraints import ConstraintOp
from ..constraints import infer_constraints
from ..join import join_types
from ..join import structural_join_types
from ..meet import meet_types
from ..meet import structural_meet_types
from ..solve import solve_constraints
from ..substitute import substitute_type
from ..subtypes import is_same_type
from ..subtypes import is_structural_subtype
from ..subtypes import is_structurally_equivalent
from ..subtypes import is_subtype
from ..symbols import ArgKind
from ..symbols import TypeAlias
from ..symbols import TypeInfo
from ..symbols import VarianceKind
from ..types import CallableType
from ..types import Instance
from ..types import TupleType
from ..types import Type
from ..types import TypeAliasType
from ..types import TypeType
from ..types import TypeVarLikeType
from ..types import UnionType
from .helpers import make_any
from .helpers import make_info
from .helpers import make_instance
from .helpers import make_recursive_json_like_alias_case
from .helpers import make_recursive_mixed_tuple_alias_case
from .helpers import make_type_var
from .helpers import make_typed_dict


##


def make_nominal_subtype_pair() -> tuple[Instance, Instance]:
    base_info = make_info('Base')
    child_info = make_info('Child')
    child_info._mro = (child_info, base_info)
    return make_instance(child_info), make_instance(base_info)


def assert_nominal_subtype_lattice_law(subtype: Type, supertype: Type) -> None:
    assert is_subtype(subtype, supertype)
    assert is_same_type(join_types(subtype, supertype), supertype)
    assert is_same_type(join_types(supertype, subtype), supertype)
    assert is_same_type(meet_types(subtype, supertype), subtype)
    assert is_same_type(meet_types(supertype, subtype), subtype)


def assert_nominal_lattice_commutes(left: Type, right: Type) -> None:
    assert is_same_type(join_types(left, right), join_types(right, left))
    assert is_same_type(meet_types(left, right), meet_types(right, left))


def assert_nominal_lattice_absorbs(left: Type, right: Type) -> None:
    assert is_same_type(meet_types(left, join_types(left, right)), left)
    assert is_same_type(join_types(left, meet_types(left, right)), left)


def assert_structural_subtype_lattice_law(subtype: Type, supertype: Type) -> None:
    assert is_structural_subtype(subtype, supertype)
    assert is_structurally_equivalent(structural_join_types(subtype, supertype), supertype)
    assert is_structurally_equivalent(structural_join_types(supertype, subtype), supertype)
    assert is_structurally_equivalent(structural_meet_types(subtype, supertype), subtype)
    assert is_structurally_equivalent(structural_meet_types(supertype, subtype), subtype)


def assert_structural_lattice_commutes(left: Type, right: Type) -> None:
    assert is_structurally_equivalent(
        structural_join_types(left, right),
        structural_join_types(right, left),
    )
    assert is_structurally_equivalent(
        structural_meet_types(left, right),
        structural_meet_types(right, left),
    )


def assert_constraints_reconstruct(
        template: Type,
        actual: Type,
        variables: list[TypeVarLikeType],
        *,
        structural: bool = False,
) -> None:
    constraints = infer_constraints(template, actual, ConstraintOp.SUPERTYPE_OF)
    solution = solve_constraints(variables, constraints)

    mapping: dict[TypeVarLikeType, Type] = {}
    for variable, item in zip(variables, solution):
        assert item is not None
        mapping[variable] = item

    substituted = substitute_type(template, mapping)
    if structural:
        assert is_structurally_equivalent(substituted, actual)
    else:
        assert is_same_type(substituted, actual)


##


def test_nominal_subtype_lattice_laws_cover_supported_shapes() -> None:
    child, base = make_nominal_subtype_pair()

    assert_nominal_subtype_lattice_law(child, base)
    assert_nominal_subtype_lattice_law(TypeType(child), TypeType(base))

    box_info = TypeInfo('Box', 'Box', variances=[VarianceKind.CO])
    assert_nominal_subtype_lattice_law(
        make_instance(box_info, [child]),
        make_instance(box_info, [base]),
    )

    other = make_instance(make_info('Other'))
    assert_nominal_subtype_lattice_law(child, UnionType([base, other]))

    assert_nominal_subtype_lattice_law(
        make_typed_dict({'value': child, 'extra': child}, {'value', 'extra'}),
        make_typed_dict({'value': child}, {'value'}),
    )

    fallback = make_instance(make_info('function'))
    more_specific = CallableType([base], [ArgKind.POS], [None], child, fallback)
    more_general = CallableType([child], [ArgKind.POS], [None], base, fallback)
    assert_nominal_subtype_lattice_law(more_specific, more_general)


def test_nominal_lattice_commutativity_covers_supported_shapes() -> None:
    child, base = make_nominal_subtype_pair()
    other = make_instance(make_info('Other'))
    tuple_fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    fallback = make_instance(make_info('function'))

    cases = [
        (child, base),
        (child, other),
        (
            TupleType([child, other], tuple_fallback),
            TupleType([base, other], tuple_fallback),
        ),
        (
            CallableType([base], [ArgKind.POS], [None], child, fallback),
            CallableType([child], [ArgKind.POS], [None], base, fallback),
        ),
        (TypeType(child), TypeType(base)),
    ]

    for left, right in cases:
        assert_nominal_lattice_commutes(left, right)


def test_nominal_lattice_absorption_covers_instances_and_unions() -> None:
    child, base = make_nominal_subtype_pair()
    other = make_instance(make_info('Other'))

    assert_nominal_lattice_absorbs(child, base)
    assert_nominal_lattice_absorbs(child, other)
    assert_nominal_lattice_absorbs(child, UnionType([base, other]))


def test_structural_alias_lattice_laws_ignore_nonrecursive_alias_identity() -> None:
    int_type = make_instance(make_info('builtins.int'))
    list_info = make_info('builtins.list')
    target = make_instance(list_info, [int_type])
    alias = TypeAlias('IntList', target)
    alias_type = TypeAliasType(alias, [])

    assert_structural_subtype_lattice_law(alias_type, target)
    assert_structural_subtype_lattice_law(target, alias_type)
    assert_structural_lattice_commutes(alias_type, target)


def test_structural_recursive_alias_lattice_laws_ignore_alias_identity() -> None:
    left = make_recursive_json_like_alias_case('Jsonish')
    right = make_recursive_json_like_alias_case(
        'OtherJsonish',
        reverse_union=True,
        list_info=left.list_info,
        dict_info=left.dict_info,
        bool_type=left.bool_type,
        int_type=left.int_type,
        str_type=left.str_type,
    )

    assert_structural_subtype_lattice_law(left.alias_type, left.one_unrolling)
    assert_structural_subtype_lattice_law(left.one_unrolling, left.alias_type)
    assert_structural_subtype_lattice_law(left.alias_type, right.alias_type)
    assert_structural_lattice_commutes(left.alias_type, left.one_unrolling)
    assert_structural_lattice_commutes(left.alias_type, right.alias_type)


def test_structural_directional_recursive_subtype_lattice_law() -> None:
    list_info = make_info('builtins.list')
    list_info._variances = (VarianceKind.CO,)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    left_alias = TypeAlias('Left', make_any())
    right_alias = TypeAlias('Right', make_any())
    left_alias_type = TypeAliasType(left_alias, [])
    right_alias_type = TypeAliasType(right_alias, [])
    left_alias._target = UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = UnionType([int_type, str_type, make_instance(list_info, [right_alias_type])])

    assert not is_structurally_equivalent(left_alias_type, right_alias_type)
    assert is_structural_subtype(left_alias_type, right_alias_type)
    assert not is_structural_subtype(right_alias_type, left_alias_type)
    assert_structural_subtype_lattice_law(left_alias_type, right_alias_type)


def test_solve_solution_satisfies_nominal_bounds() -> None:
    object_info = make_info('builtins.object')
    int_info = make_info('builtins.int')
    str_info = make_info('builtins.str')
    int_info._mro = (int_info, object_info)
    str_info._mro = (str_info, object_info)
    object_type = make_instance(object_info)
    int_type = make_instance(int_info)
    str_type = make_instance(str_info)
    t_var = make_type_var('T', 1)

    solution = solve_constraints(
        [t_var],
        [
            Constraint(t_var, ConstraintOp.SUPERTYPE_OF, int_type),
            Constraint(t_var, ConstraintOp.SUPERTYPE_OF, str_type),
            Constraint(t_var, ConstraintOp.SUBTYPE_OF, object_type),
        ],
    )[0]

    assert solution is not None
    assert is_subtype(int_type, solution)
    assert is_subtype(str_type, solution)
    assert is_subtype(solution, object_type)


def test_constraint_solution_reconstructs_generic_instance_tuple_and_callable_shapes() -> None:
    t_var = make_type_var('T', 1)
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    box_info = TypeInfo(
        'Box',
        'Box',
        type_vars=[t_var],
        variances=[VarianceKind.CO],
    )
    assert_constraints_reconstruct(
        make_instance(box_info, [t_var]),
        make_instance(box_info, [int_type]),
        [t_var],
    )

    tuple_fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    assert_constraints_reconstruct(
        TupleType([t_var, str_type], tuple_fallback),
        TupleType([int_type, str_type], tuple_fallback),
        [t_var],
    )

    fallback = make_instance(make_info('function'))
    assert_constraints_reconstruct(
        CallableType([t_var], [ArgKind.POS], [None], t_var, fallback),
        CallableType([int_type], [ArgKind.POS], [None], int_type, fallback),
        [t_var],
    )


def test_constraint_solution_reconstructs_recursive_mixed_variadic_alias_shape() -> None:
    case = make_recursive_mixed_tuple_alias_case('MixedNode', 1, 2)

    assert_constraints_reconstruct(
        case.alias_type,
        case.one_unrolling,
        [case.type_var, case.type_var_tuple],
        structural=True,
    )
