# ruff: noqa: PLC0132 SLF001
import dataclasses as dc
import typing as ta

import pytest

from ...errors import ReflectionError
from ...reflect import RuntimeTypeReflector
from ...universe import RuntimeTypeUniverse
from .. import symbols
from .. import types
from ..subtypes import is_alpha_structurally_equivalent
from ..subtypes import is_structurally_equivalent
from ..typekeys import TypeKeyPolicy
from ..typekeys import _tuple_type_key
from ..typekeys import _tuple_type_key_or_none
from ..typekeys import _type_key_with_policy_or_none
from ..typekeys import alpha_structural_type_key
from ..typekeys import alpha_structural_type_key_or_none
from ..typekeys import alpha_type_key
from ..typekeys import alpha_type_key_or_none
from ..typekeys import structural_type_key
from ..typekeys import structural_type_key_or_none
from ..typekeys import tuple_type_key_with_policy
from ..typekeys import tuple_type_key_with_policy_or_none
from ..typekeys import type_key
from ..typekeys import type_key_or_none
from ..typekeys import type_key_with_policy
from ..typekeys import type_key_with_policy_or_none
from .helpers import make_any
from .helpers import make_info
from .helpers import make_instance
from .helpers import make_recursive_variadic_tuple_alias_case
from .helpers import make_type_var


def test_string_type_key_simple_supported_nodes_are_explicit() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bool_type = make_instance(make_info('builtins.bool'))
    bytes_type = make_instance(make_info('builtins.bytes'))
    tuple_type = make_instance(make_info('builtins.tuple'))
    function_type = make_instance(make_info('collections.abc.Callable'))

    cases = [
        (types.TypeGuardedType(int_type), "I['builtins.int']"),
        (types.AnnotatedType(int_type, ('cfg',)), ("Ann[I['builtins.int'],$0]", ('cfg',))),
        (types.RequiredType(int_type), "Req[True,I['builtins.int']]"),
        (types.RequiredType(int_type, required=False), "Req[False,I['builtins.int']]"),
        (types.ReadOnlyType(int_type), "RO[I['builtins.int']]"),
        (make_type_var('T', 1), 'TV[1]'),
        (
            types.ParamSpecType('P', 'P', types.TypeVarId(2), make_any(), make_any()),
            'PS[2]',
        ),
        (
            types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(3), make_any(), make_any(), tuple_type),
            'TVT[3]',
        ),
        (
            types.TypeVarType(
                'T',
                'T',
                types.TypeVarId(4, meta_level=2, namespace='scope'),
                [],
                make_any(),
                make_any(),
            ),
            "TV[4,ns,'scope',meta,2]",
        ),
        (types.UnboundType('Box', [int_type]), "Unbound['Box',I['builtins.int']]"),
        (types.CallableArgument(int_type, 'value'), "CA[I['builtins.int'],name,'value']"),
        (
            types.CallableArgument(int_type, 'value', 'Arg'),
            "CA[I['builtins.int'],name,'value',ctor,'Arg']",
        ),
        (types.TypeList([int_type, str_type]), "TL[I['builtins.int'],I['builtins.str']]"),
        (types.UnpackType(tuple_type), "Unpack[I['builtins.tuple']]"),
        (make_any(), 'Any'),
        (types.UninhabitedType(), 'Never'),
        (types.NoneType(), 'None'),
        (types.ErasedType(), 'Erased'),
        (types.DeletedType(), 'Deleted'),
        (types.DeletedType('x'), "Deleted['x']"),
        (int_type, "I['builtins.int']"),
        (
            types.Parameters([int_type], [symbols.ArgKind.NAMED_OPT], ['value']),
            "P[I['builtins.int'],k[NAMED_OPT],n['value']]",
        ),
        (
            types.TupleType([int_type, str_type], tuple_type),
            "Tuple[I['builtins.int'],I['builtins.str'],I['builtins.tuple']]",
        ),
        (
            types.TypedDictType(
                {'b': str_type, 'a': int_type},
                {'a'},
                {'b'},
                make_instance(make_info('builtins.dict'), [str_type, int_type]),
            ),
            (
                "TD[i['a',I['builtins.int']],i['b',I['builtins.str']],req['a'],ro['b'],"
                "f[I['builtins.dict',I['builtins.str'],I['builtins.int']]]]"
            ),
        ),
        (types.RawExpressionType(42, 'builtins.int'), "Raw[int:42,'builtins.int']"),
        (types.RawExpressionType(None, 'builtins.object'), "Raw[None,'builtins.object']"),
        (types.LiteralType(None, make_instance(make_info('builtins.None'))), "L[None:,I['builtins.None']]"),
        (types.LiteralType(True, bool_type), "L[bool:True,I['builtins.bool']]"),
        (types.LiteralType(42, int_type), "L[int:42,I['builtins.int']]"),
        (types.LiteralType('x', str_type), "L[str:'x',I['builtins.str']]"),
        (types.LiteralType(b'ab', bytes_type), "L[bytes:b'ab',I['builtins.bytes']]"),
        (types.UnionType([str_type, int_type]), "U[I['builtins.int'],I['builtins.str']]"),
        (types.EllipsisType(), 'Ellipsis'),
        (types.TypeType(int_type), "Type[I['builtins.int']]"),
        (types.PlaceholderType('Future', [int_type]), "Placeholder['Future',I['builtins.int']]"),
        (
            types.CallableType([int_type], [symbols.ArgKind.POS], [None], str_type, function_type),
            (
                "C[I['builtins.int'],k[POS],n[None],r[I['builtins.str']],"
                "f[I['collections.abc.Callable']]]"
            ),
        ),
        (
            types.CallableType(
                [int_type],
                [symbols.ArgKind.NAMED],
                ['x'],
                str_type,
                function_type,
                is_ellipsis_args=True,
            ),
            (
                "C[I['builtins.int'],k[NAMED],n['x'],r[I['builtins.str']],"
                "f[I['collections.abc.Callable']],ellipsis]"
            ),
        ),
    ]

    for typ, expected in cases:
        assert type_key(typ) == expected


def test_string_type_key_common_combinations_are_explicit() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    list_type = make_instance(make_info('builtins.list'), [int_type])
    sequence_type = make_instance(make_info('collections.abc.Sequence'), [int_type])
    mapping_type = make_instance(make_info('collections.abc.Mapping'), [str_type, sequence_type])

    assert type_key(list_type) == "I['builtins.list',I['builtins.int']]"
    assert type_key(mapping_type) == (
        "I['collections.abc.Mapping',I['builtins.str'],"
        "I['collections.abc.Sequence',I['builtins.int']]]"
    )

    literal_union = types.UnionType([
        types.LiteralType('red', str_type),
        types.LiteralType('blue', str_type),
        types.NoneType(),
    ])

    assert type_key(literal_union) == (
        "U[L[str:'blue',I['builtins.str']],L[str:'red',I['builtins.str']],None]"
    )


def test_type_key_instances_use_type_fullname_and_arg_keys() -> None:
    box_info = make_info('Box')

    assert type_key(make_instance(box_info, [make_any()])) == type_key(make_instance(box_info, [make_any()]))
    assert type_key(make_instance(box_info, [make_any()])) != type_key(make_instance(box_info, [types.NoneType()]))
    assert type_key(make_instance(box_info, [make_any()])) == "I['Box',Any]"


def test_type_key_unions_are_order_insensitive() -> None:
    left = types.UnionType([make_instance(make_info('int')), make_instance(make_info('str'))])
    right = types.UnionType([make_instance(make_info('str')), make_instance(make_info('int'))])

    assert type_key(left) == type_key(right)
    assert type_key(left) == "U[I['int'],I['str']]"


def test_type_key_scalar_literal_union_uses_explicit_kind_order() -> None:
    bool_type = make_instance(make_info('builtins.bool'))
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    bytes_type = make_instance(make_info('builtins.bytes'))
    typ = types.UnionType([
        types.LiteralType(b'ab', bytes_type),
        types.LiteralType('x', str_type),
        types.LiteralType(2, int_type),
        types.LiteralType(1, int_type),
        types.LiteralType(True, bool_type),
        types.LiteralType(None, make_instance(make_info('builtins.None'))),
    ])

    assert type_key(typ) == (
        "U[L[None:,I['builtins.None']],"
        "L[bool:True,I['builtins.bool']],"
        "L[int:1,I['builtins.int']],"
        "L[int:2,I['builtins.int']],"
        "L[str:'x',I['builtins.str']],"
        "L[bytes:b'ab',I['builtins.bytes']]]"
    )


def test_type_key_none_literal_is_distinct_from_none_type() -> None:
    none_literal = types.LiteralType(None, make_instance(make_info('builtins.None')))

    assert type_key(none_literal) == "L[None:,I['builtins.None']]"
    assert type_key(none_literal) != type_key(types.NoneType())


def test_type_key_literals_include_value_type() -> None:
    bool_info = make_info('bool')
    int_info = make_info('int')

    assert type_key(types.LiteralType(True, make_instance(bool_info))) != type_key(
        types.LiteralType(1, make_instance(int_info)),
    )


def test_type_key_type_vars_use_ids_not_alpha_equivalence() -> None:
    assert type_key(make_type_var('T', 1)) == type_key(make_type_var('U', 1))
    assert type_key(make_type_var('T', 1)) != type_key(make_type_var('U', 2))


def test_alpha_type_key_canonicalizes_type_var_ids() -> None:
    assert alpha_type_key(make_type_var('T', 1)) == alpha_type_key(make_type_var('U', 2))


def test_alpha_type_key_preserves_repeated_type_var_positions() -> None:
    pair_info = make_info('Pair')
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)
    right_v = make_type_var('V', 3)

    left = make_instance(pair_info, [left_t, left_t])
    consistent = make_instance(pair_info, [right_u, right_u])
    inconsistent = make_instance(pair_info, [right_u, right_v])

    assert alpha_type_key(left) == alpha_type_key(consistent)
    assert alpha_type_key(left) != alpha_type_key(inconsistent)


def test_alpha_type_key_canonicalizes_callable_type_vars() -> None:
    fallback = make_instance(make_info('function'))
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)
    right_v = make_type_var('V', 3)

    left = types.CallableType([left_t], [symbols.ArgKind.POS], [None], left_t, fallback)
    consistent = types.CallableType([right_u], [symbols.ArgKind.POS], [None], right_u, fallback)
    inconsistent = types.CallableType([right_u], [symbols.ArgKind.POS], [None], right_v, fallback)

    assert alpha_type_key(left) == alpha_type_key(consistent)
    assert alpha_type_key(left) != alpha_type_key(inconsistent)


def test_type_key_policy_supports_dc_replace() -> None:
    policy = TypeKeyPolicy()

    assert dc.replace(policy, alpha=True).alpha
    assert repr(policy) == (
        'TypeKeyPolicy('
        'alpha=False, '
        'structural=False, '
        'include_annotated_metadata=True, '
        'preserve_alias_identity=True, '
        'preserve_newtype_identity=True)'
    )


def test_type_key_with_policy_matches_existing_presets() -> None:
    typ = types.AnnotatedType(make_instance(make_info('builtins.int')), ('cfg',))

    assert type_key_with_policy(typ, TypeKeyPolicy()) == type_key(typ)
    assert type_key_with_policy_or_none(typ, TypeKeyPolicy(structural=True, include_annotated_metadata=False)) == (
        structural_type_key(typ)
    )


def test_tuple_type_key_with_policy_matches_existing_tuple_preset() -> None:
    typ = types.AnnotatedType(make_instance(make_info('builtins.int')), ('cfg',))

    assert tuple_type_key_with_policy(typ, TypeKeyPolicy()) == _tuple_type_key(typ)
    assert tuple_type_key_with_policy(typ, TypeKeyPolicy(include_annotated_metadata=False)) == (
        'instance',
        'builtins.int',
        (),
        (),
    )


def test_type_key_with_policy_fails_closed_for_unsupported_nodes() -> None:
    typ = types.PartialType(None, None)
    policy = TypeKeyPolicy(
        alpha=True,
        structural=True,
        include_annotated_metadata=False,
        preserve_alias_identity=False,
        preserve_newtype_identity=False,
    )

    assert type_key_with_policy_or_none(typ, policy) is None
    assert tuple_type_key_with_policy_or_none(typ, policy) is None
    with pytest.raises(ReflectionError, match='not implemented'):
        type_key_with_policy(typ, policy)
    with pytest.raises(ReflectionError, match='not implemented'):
        tuple_type_key_with_policy(typ, policy)


def test_type_key_policy_can_ignore_annotated_metadata_without_structural_keying() -> None:
    item = make_instance(make_info('builtins.int'))
    typ = types.AnnotatedType(item, ([],))

    assert type_key_or_none(typ) is None
    assert _type_key_with_policy_or_none(typ, TypeKeyPolicy(include_annotated_metadata=False)) == type_key(item)


def test_type_key_policy_can_preserve_annotated_metadata_with_structural_keying() -> None:
    item = make_instance(make_info('builtins.int'))
    typ = types.AnnotatedType(item, ('cfg',))
    policy = TypeKeyPolicy(
        structural=True,
        include_annotated_metadata=True,
        preserve_alias_identity=False,
    )

    assert _type_key_with_policy_or_none(typ, policy) == type_key(typ)
    assert _type_key_with_policy_or_none(typ, policy) != structural_type_key(item)


def test_type_key_policy_can_erase_alias_identity_without_structural_keying() -> None:
    target = make_instance(make_info('builtins.list'), [make_instance(make_info('builtins.int'))])
    left_alias = symbols.TypeAlias('Left', target, runtime_object=object())
    right_alias = symbols.TypeAlias('Right', target, runtime_object=object())
    policy = TypeKeyPolicy(preserve_alias_identity=False)

    assert type_key(types.TypeAliasType(left_alias, [])) != type_key(types.TypeAliasType(right_alias, []))
    assert _type_key_with_policy_or_none(types.TypeAliasType(left_alias, []), policy) == type_key(target)
    assert _type_key_with_policy_or_none(types.TypeAliasType(left_alias, []), policy) == (
        _type_key_with_policy_or_none(types.TypeAliasType(right_alias, []), policy)
    )


def test_type_key_policy_can_preserve_alias_identity_with_structural_keying() -> None:
    target = make_instance(make_info('builtins.list'), [make_instance(make_info('builtins.int'))])
    left_alias = symbols.TypeAlias('Left', target, runtime_object=object())
    right_alias = symbols.TypeAlias('Right', target, runtime_object=object())
    policy = TypeKeyPolicy(
        structural=True,
        include_annotated_metadata=False,
        preserve_alias_identity=True,
    )

    assert _type_key_with_policy_or_none(types.TypeAliasType(left_alias, []), policy) != structural_type_key(target)
    assert _type_key_with_policy_or_none(types.TypeAliasType(left_alias, []), policy) != (
        _type_key_with_policy_or_none(types.TypeAliasType(right_alias, []), policy)
    )


def test_type_key_policy_structural_recursive_alias_canonicalization_is_alias_policy_dependent() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    one_unrolling = types.UnionType([int_type, make_instance(list_info, [alias_type])])
    alias._target = one_unrolling
    structural_preserving_alias = TypeKeyPolicy(
        structural=True,
        include_annotated_metadata=False,
        preserve_alias_identity=True,
    )

    assert structural_type_key(alias_type) == structural_type_key(one_unrolling)
    assert _type_key_with_policy_or_none(alias_type, structural_preserving_alias) != (
        _type_key_with_policy_or_none(one_unrolling, structural_preserving_alias)
    )


def test_type_key_policy_can_erase_core_newtype_identity_when_supertype_is_recorded() -> None:
    int_type = make_instance(make_info('builtins.int'))
    user_info = make_info('example.UserId')
    account_info = make_info('example.AccountId')
    user_info._new_type_supertype = int_type
    account_info._new_type_supertype = int_type
    user_id = make_instance(user_info)
    account_id = make_instance(account_info)
    policy = TypeKeyPolicy(preserve_newtype_identity=False)

    assert type_key(user_id) != type_key(account_id)
    assert type_key(user_id) != type_key(int_type)
    assert _type_key_with_policy_or_none(user_id, policy) == type_key(int_type)
    assert _type_key_with_policy_or_none(account_id, policy) == type_key(int_type)


def test_type_key_policy_preserves_newtype_identity_by_default() -> None:
    int_type = make_instance(make_info('builtins.int'))
    user_info = make_info('example.UserId')
    user_info._new_type_supertype = int_type
    user_id = make_instance(user_info)

    assert type_key(user_id) == _type_key_with_policy_or_none(user_id, TypeKeyPolicy())
    assert type_key(user_id) != type_key(int_type)


def test_reflected_type_key_policy_can_erase_newtype_identity() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore
    account_id = ta.NewType('AccountId', int)  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    user_type = reflector.reflect_type(user_id)
    account_type = reflector.reflect_type(account_id)
    int_type = reflector.reflect_type(int)
    policy = TypeKeyPolicy(preserve_newtype_identity=False)

    assert isinstance(user_type, types.Instance)
    assert user_type.type.new_type_supertype == int_type
    assert type_key(user_type) != type_key(account_type)
    assert _type_key_with_policy_or_none(user_type, policy) == type_key(int_type)
    assert _type_key_with_policy_or_none(account_type, policy) == type_key(int_type)


def test_reflected_type_key_policy_can_erase_literal_backed_newtype_identity() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    mode_type = reflector.reflect_type(mode)
    other_mode_type = reflector.reflect_type(other_mode)
    literal_type = reflector.reflect_type(ta.Literal['a', 'b'])
    policy = TypeKeyPolicy(preserve_newtype_identity=False)

    assert isinstance(mode_type, types.Instance)
    assert mode_type.type.new_type_supertype == literal_type
    assert type_key(mode_type) != type_key(other_mode_type)
    assert type_key(mode_type) != type_key(literal_type)
    assert _type_key_with_policy_or_none(mode_type, policy) == type_key(literal_type)
    assert _type_key_with_policy_or_none(other_mode_type, policy) == type_key(literal_type)


def test_type_key_policy_composes_annotation_alias_and_newtype_knobs() -> None:
    int_type = make_instance(make_info('builtins.int'))
    user_info = make_info('example.UserId')
    user_info._new_type_supertype = int_type
    user_id = make_instance(user_info)
    alias = symbols.TypeAlias('UserAlias', user_id, runtime_object=object())
    typ = types.AnnotatedType(types.TypeAliasType(alias, []), ('cfg',))
    policy = TypeKeyPolicy(
        include_annotated_metadata=True,
        preserve_alias_identity=False,
        preserve_newtype_identity=False,
    )

    assert type_key_with_policy(typ, policy) == (
        "Ann[I['builtins.int'],$0]",
        ('cfg',),
    )
    assert type_key_with_policy(typ, policy) != type_key_with_policy(
        typ,
        dc.replace(policy, include_annotated_metadata=False),
    )
    assert type_key_with_policy(typ, policy) != type_key_with_policy(
        typ,
        dc.replace(policy, preserve_alias_identity=True),
    )
    assert type_key_with_policy(typ, policy) != type_key_with_policy(
        typ,
        dc.replace(policy, preserve_newtype_identity=True),
    )


def test_structural_type_key_strips_annotated_metadata() -> None:
    item = make_instance(make_info('builtins.int'))

    assert structural_type_key(types.AnnotatedType(item, ('cfg',))) == structural_type_key(item)
    assert structural_type_key(types.AnnotatedType(item, ([],))) == structural_type_key(item)
    assert type_key_or_none(types.AnnotatedType(item, ([],))) is None


def test_structural_type_key_erases_nonrecursive_alias_identity() -> None:
    target = make_instance(make_info('builtins.list'), [make_instance(make_info('builtins.int'))])
    left_alias = symbols.TypeAlias('Alias', target, runtime_object=object())
    right_alias = symbols.TypeAlias('Alias', target, runtime_object=object())

    assert type_key(types.TypeAliasType(left_alias, [])) != type_key(types.TypeAliasType(right_alias, []))
    assert structural_type_key(types.TypeAliasType(left_alias, [])) == structural_type_key(target)
    assert structural_type_key(types.TypeAliasType(left_alias, [])) == structural_type_key(
        types.TypeAliasType(right_alias, []),
    )


def test_type_key_parameterized_variadic_alias_includes_packed_tuple_arg() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_type = make_instance(make_info('builtins.tuple'))
    type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), tuple_type)
    alias = symbols.TypeAlias(
        'Alias',
        types.TupleType([types.UnpackType(type_var_tuple)], tuple_type),
        alias_tvars=[type_var_tuple],
        runtime_object=object(),
    )
    alias_type = types.TypeAliasType(alias, [types.TupleType([int_type, str_type], tuple_type)])
    packed_key = (
        'tuple',
        (('instance', 'builtins.int', (), ()), ('instance', 'builtins.str', (), ())),
        ('instance', 'builtins.tuple', (), ()),
    )

    assert type_key(alias_type) == (
        "A['Alias',$0,Tuple[I['builtins.int'],I['builtins.str'],I['builtins.tuple']],"
        "Tuple[I['builtins.int'],I['builtins.str'],I['builtins.tuple']]]",
        alias.runtime_object,
    )
    assert _tuple_type_key(alias_type) == (
        'type_alias',
        'Alias',
        alias.runtime_object,
        (packed_key,),
        packed_key,
    )


def test_structural_type_key_erases_variadic_alias_identity_but_preserves_packed_tuple_arg() -> None:
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    tuple_type = make_instance(make_info('builtins.tuple'))
    left_type_var_tuple = types.TypeVarTupleType('Ts', 'Ts', types.TypeVarId(1), make_any(), make_any(), tuple_type)
    right_type_var_tuple = types.TypeVarTupleType('Us', 'Us', types.TypeVarId(2), make_any(), make_any(), tuple_type)
    left_alias = symbols.TypeAlias(
        'Left',
        types.TupleType([types.UnpackType(left_type_var_tuple)], tuple_type),
        alias_tvars=[left_type_var_tuple],
        runtime_object=object(),
    )
    right_alias = symbols.TypeAlias(
        'Right',
        types.TupleType([types.UnpackType(right_type_var_tuple)], tuple_type),
        alias_tvars=[right_type_var_tuple],
        runtime_object=object(),
    )
    packed_arg = types.TupleType([int_type, str_type], tuple_type)
    target = types.TupleType([int_type, str_type], tuple_type)

    assert type_key(types.TypeAliasType(left_alias, [packed_arg])) != (
        type_key(types.TypeAliasType(right_alias, [packed_arg]))
    )
    assert structural_type_key(types.TypeAliasType(left_alias, [packed_arg])) == structural_type_key(target)
    assert structural_type_key(types.TypeAliasType(left_alias, [packed_arg])) == structural_type_key(
        types.TypeAliasType(right_alias, [packed_arg]),
    )


def test_structural_type_key_preserves_new_type_identity() -> None:
    left_new_type = make_instance(make_info('example.UserId'))
    right_new_type = make_instance(make_info('example.AccountId'))
    left_alias = symbols.TypeAlias('LeftAlias', left_new_type)
    right_alias = symbols.TypeAlias('RightAlias', right_new_type)

    assert structural_type_key(types.TypeAliasType(left_alias, [])) == structural_type_key(left_new_type)
    assert structural_type_key(types.TypeAliasType(left_alias, [])) != structural_type_key(right_new_type)
    assert structural_type_key(types.TypeAliasType(left_alias, [])) != structural_type_key(
        types.TypeAliasType(right_alias, []),
    )


def test_alpha_structural_type_key_canonicalizes_alias_target_type_vars() -> None:
    list_info = make_info('builtins.list')
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)
    left_alias = symbols.TypeAlias('Left', make_instance(list_info, [left_t]), alias_tvars=[left_t])
    right_alias = symbols.TypeAlias('Right', make_instance(list_info, [right_u]), alias_tvars=[right_u])

    assert structural_type_key(types.TypeAliasType(left_alias, [left_t])) != structural_type_key(
        types.TypeAliasType(right_alias, [right_u]),
    )
    assert alpha_structural_type_key(types.TypeAliasType(left_alias, [left_t])) == alpha_structural_type_key(
        types.TypeAliasType(right_alias, [right_u]),
    )


def test_type_key_annotated_includes_metadata_when_hashable() -> None:
    item = make_instance(make_info('int'))

    assert type_key(types.AnnotatedType(item, ('cfg',))) == type_key(types.AnnotatedType(item, ('cfg',)))
    assert type_key(types.AnnotatedType(item, ('cfg',))) != type_key(types.AnnotatedType(item, ('other',)))


def test_type_key_annotated_fails_closed_for_unhashable_metadata() -> None:
    typ = types.AnnotatedType(make_instance(make_info('int')), ([],))

    assert type_key_or_none(typ) is None


def test_type_key_callables_include_arg_shape_return_and_ellipsis() -> None:
    fallback = make_instance(make_info('function'))
    arg = make_instance(make_info('int'))
    ret = make_instance(make_info('str'))

    left = types.CallableType([arg], [symbols.ArgKind.POS], [None], ret, fallback)
    same = types.CallableType([arg], [symbols.ArgKind.POS], [None], ret, fallback)
    different = types.CallableType([arg], [symbols.ArgKind.POS], ['x'], ret, fallback)

    assert type_key(left) == type_key(same)
    assert type_key(left) != type_key(different)
    assert type_key(left) != type_key(
        types.CallableType([arg], [symbols.ArgKind.POS], [None], ret, fallback, is_ellipsis_args=True),
    )


def test_type_key_overloaded_callables_preserve_item_order() -> None:
    fallback = make_instance(make_info('collections.abc.Callable'))
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    int_item = types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback)
    str_item = types.CallableType([str_type], [symbols.ArgKind.POS], [None], str_type, fallback)

    left = types.Overloaded([int_item, str_item])
    same = types.Overloaded([int_item, str_item])
    reversed_items = types.Overloaded([str_item, int_item])

    assert type_key(left) == type_key(same)
    assert type_key(left) != type_key(reversed_items)
    assert type_key(left) == (
        "O[C[I['builtins.int'],k[POS],n[None],r[I['builtins.int']],"
        "f[I['collections.abc.Callable']]],"
        "C[I['builtins.str'],k[POS],n[None],r[I['builtins.str']],"
        "f[I['collections.abc.Callable']]]]"
    )
    assert _tuple_type_key(left)[0] == 'overloaded'


def test_type_key_aliases_support_direct_recursive_alias() -> None:
    alias = symbols.TypeAlias('Alias', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = alias_type

    assert type_key_or_none(alias_type) == 'RA[AR[0]]'
    assert _tuple_type_key_or_none(alias_type) == (
        'recursive_type_alias',
        (),
        ('type_alias_ref', 0, ()),
    )


def test_type_key_recursive_aliases_ignore_alias_names() -> None:
    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([types.NoneType(), left_alias_type])
    right_alias._target = types.UnionType([types.NoneType(), right_alias_type])

    assert type_key(left_alias_type) == type_key(right_alias_type)


def test_type_key_indirect_recursive_aliases_use_stable_backrefs() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')
    str_type = make_instance(make_info('builtins.str'))

    alias_a = symbols.TypeAlias('A', make_any())
    alias_b = symbols.TypeAlias('B', make_any())
    alias_a_type = types.TypeAliasType(alias_a, [])
    alias_b_type = types.TypeAliasType(alias_b, [])
    alias_a._target = make_instance(list_info, [alias_b_type])
    alias_b._target = make_instance(dict_info, [str_type, alias_a_type])

    assert _tuple_type_key(alias_a_type) == (
        'recursive_type_alias',
        (),
        (
            'instance',
            'builtins.list',
            (
                (
                    'recursive_type_alias',
                    (),
                    (
                        'instance',
                        'builtins.dict',
                        (
                            ('instance', 'builtins.str', (), ()),
                            ('type_alias_ref', 0, ()),
                        ),
                        (),
                    ),
                ),
            ),
            (),
        ),
    )


def test_type_key_indirect_recursive_aliases_ignore_alias_names() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')
    str_type = make_instance(make_info('builtins.str'))

    left_a = symbols.TypeAlias('LeftA', make_any())
    left_b = symbols.TypeAlias('LeftB', make_any())
    right_a = symbols.TypeAlias('RightA', make_any())
    right_b = symbols.TypeAlias('RightB', make_any())

    left_a_type = types.TypeAliasType(left_a, [])
    left_b_type = types.TypeAliasType(left_b, [])
    right_a_type = types.TypeAliasType(right_a, [])
    right_b_type = types.TypeAliasType(right_b, [])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [str_type, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [str_type, right_a_type])

    assert type_key(left_a_type) == type_key(right_a_type)


def test_type_key_indirect_recursive_aliases_still_compare_structure() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')
    str_type = make_instance(make_info('builtins.str'))
    int_type = make_instance(make_info('builtins.int'))

    left_a = symbols.TypeAlias('LeftA', make_any())
    left_b = symbols.TypeAlias('LeftB', make_any())
    right_a = symbols.TypeAlias('RightA', make_any())
    right_b = symbols.TypeAlias('RightB', make_any())

    left_a_type = types.TypeAliasType(left_a, [])
    left_b_type = types.TypeAliasType(left_b, [])
    right_a_type = types.TypeAliasType(right_a, [])
    right_b_type = types.TypeAliasType(right_b, [])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [str_type, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [int_type, right_a_type])

    assert type_key(left_a_type) != type_key(right_a_type)


def test_type_key_mutually_recursive_alias_graphs_compare_from_corresponding_entrypoint() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')
    str_type = make_instance(make_info('builtins.str'))

    left_a = symbols.TypeAlias('LeftA', make_any())
    left_b = symbols.TypeAlias('LeftB', make_any())
    right_a = symbols.TypeAlias('RightA', make_any())
    right_b = symbols.TypeAlias('RightB', make_any())

    left_a_type = types.TypeAliasType(left_a, [])
    left_b_type = types.TypeAliasType(left_b, [])
    right_a_type = types.TypeAliasType(right_a, [])
    right_b_type = types.TypeAliasType(right_b, [])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [str_type, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [str_type, right_a_type])

    assert type_key(left_a_type) == type_key(right_a_type)
    assert type_key(left_b_type) == type_key(right_b_type)
    assert type_key(left_a_type) != type_key(left_b_type)


def test_type_key_parameterized_recursive_alias_substitutes_backref_args() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    t_var = make_type_var('T', 1)

    alias = symbols.TypeAlias('Alias', make_any(), alias_tvars=[t_var])
    alias_type = types.TypeAliasType(alias, [t_var])
    alias._target = make_instance(list_info, [alias_type])

    int_alias = types.TypeAliasType(alias, [int_type])
    str_alias = types.TypeAliasType(alias, [str_type])

    assert _tuple_type_key(int_alias) == (
        'recursive_type_alias',
        (('instance', 'builtins.int', (), ()),),
        (
            'instance',
            'builtins.list',
            (
                (
                    'type_alias_ref',
                    0,
                    (('instance', 'builtins.int', (), ()),),
                ),
            ),
            (),
        ),
    )
    assert type_key(int_alias) != type_key(str_alias)


def test_alpha_type_key_parameterized_mutual_recursion_canonicalizes_type_vars() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')

    left_t = make_type_var('T', 1)
    left_u = make_type_var('U', 2)
    right_x = make_type_var('X', 3)
    right_y = make_type_var('Y', 4)

    left_a = symbols.TypeAlias('LeftA', make_any(), alias_tvars=[left_t])
    left_b = symbols.TypeAlias('LeftB', make_any(), alias_tvars=[left_u])
    right_a = symbols.TypeAlias('RightA', make_any(), alias_tvars=[right_x])
    right_b = symbols.TypeAlias('RightB', make_any(), alias_tvars=[right_y])

    left_a_type = types.TypeAliasType(left_a, [left_t])
    left_b_type = types.TypeAliasType(left_b, [left_u])
    right_a_type = types.TypeAliasType(right_a, [right_x])
    right_b_type = types.TypeAliasType(right_b, [right_y])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [left_u, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [right_y, right_a_type])

    assert type_key(types.TypeAliasType(left_a, [left_t])) != type_key(types.TypeAliasType(right_a, [right_x]))
    assert alpha_type_key(types.TypeAliasType(left_a, [left_t])) == alpha_type_key(
        types.TypeAliasType(right_a, [right_x]),
    )
    assert alpha_type_key(types.TypeAliasType(left_b, [left_u])) == alpha_type_key(
        types.TypeAliasType(right_b, [right_y]),
    )


def test_alpha_type_key_parameterized_mutual_recursion_rejects_mismatched_backref_args() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')

    left_t = make_type_var('T', 1)
    left_u = make_type_var('U', 2)
    right_x = make_type_var('X', 3)
    right_y = make_type_var('Y', 4)

    left_a = symbols.TypeAlias('LeftA', make_any(), alias_tvars=[left_t])
    left_b = symbols.TypeAlias('LeftB', make_any(), alias_tvars=[left_u])
    right_a = symbols.TypeAlias('RightA', make_any(), alias_tvars=[right_x])
    right_b = symbols.TypeAlias('RightB', make_any(), alias_tvars=[right_y])

    left_a_type = types.TypeAliasType(left_a, [left_t])
    left_b_type = types.TypeAliasType(left_b, [left_u])
    right_a_type = types.TypeAliasType(right_a, [right_x])  # noqa
    right_b_type = types.TypeAliasType(right_b, [right_y])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [left_u, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [right_y, types.TypeAliasType(right_a, [right_y])])

    assert alpha_type_key(types.TypeAliasType(left_a, [left_t])) != alpha_type_key(
        types.TypeAliasType(right_a, [right_x]),
    )


def test_structural_type_key_recursive_alias_graphs_compare_from_corresponding_entrypoint() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')
    str_type = make_instance(make_info('builtins.str'))

    left_a = symbols.TypeAlias('LeftA', make_any())
    left_b = symbols.TypeAlias('LeftB', make_any())
    right_a = symbols.TypeAlias('RightA', make_any())
    right_b = symbols.TypeAlias('RightB', make_any())

    left_a_type = types.TypeAliasType(left_a, [])
    left_b_type = types.TypeAliasType(left_b, [])
    right_a_type = types.TypeAliasType(right_a, [])
    right_b_type = types.TypeAliasType(right_b, [])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [str_type, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [str_type, right_a_type])

    assert structural_type_key(left_a_type) == structural_type_key(right_a_type)
    assert structural_type_key(left_b_type) == structural_type_key(right_b_type)
    assert structural_type_key(left_a_type) != structural_type_key(left_b_type)


def test_structural_type_key_matches_equivalent_concrete_recursive_aliases() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)

    left_alias = symbols.TypeAlias('Left', make_any(), alias_tvars=[left_t])
    right_alias = symbols.TypeAlias('Right', make_any(), alias_tvars=[right_u])
    left_t_alias = types.TypeAliasType(left_alias, [left_t])
    right_u_alias = types.TypeAliasType(right_alias, [right_u])
    left_alias._target = types.UnionType([left_t, make_instance(list_info, [left_t_alias])])
    right_alias._target = types.UnionType([right_u, make_instance(list_info, [right_u_alias])])

    left_int = types.TypeAliasType(left_alias, [int_type])
    right_int = types.TypeAliasType(right_alias, [int_type])
    left_unrolled = types.UnionType([int_type, make_instance(list_info, [left_int])])
    right_unrolled = types.UnionType([make_instance(list_info, [right_int]), int_type])

    assert is_structurally_equivalent(left_int, right_int)
    assert is_structurally_equivalent(left_int, left_unrolled)
    assert is_structurally_equivalent(left_unrolled, right_unrolled)
    assert structural_type_key(left_int) == structural_type_key(right_int)
    assert structural_type_key(left_int) == structural_type_key(left_unrolled)
    assert structural_type_key(left_unrolled) == structural_type_key(right_unrolled)


def test_alpha_structural_type_key_matches_equivalent_generic_recursive_aliases() -> None:
    list_info = make_info('builtins.list')
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)

    left_alias = symbols.TypeAlias('Left', make_any(), alias_tvars=[left_t])
    right_alias = symbols.TypeAlias('Right', make_any(), alias_tvars=[right_u])
    left_t_alias = types.TypeAliasType(left_alias, [left_t])
    right_u_alias = types.TypeAliasType(right_alias, [right_u])
    left_alias._target = make_instance(list_info, [left_t_alias])
    right_alias._target = make_instance(list_info, [right_u_alias])

    assert is_alpha_structurally_equivalent(left_t_alias, right_u_alias)
    assert is_alpha_structurally_equivalent(left_t_alias, right_alias.target)
    assert alpha_structural_type_key(left_t_alias) == alpha_structural_type_key(right_u_alias)
    assert alpha_structural_type_key(left_t_alias) == alpha_structural_type_key(right_alias.target)


def test_structural_type_key_matches_mutual_recursive_one_unrolling() -> None:
    list_info = make_info('builtins.list')

    left_a = symbols.TypeAlias('LeftA', make_any())
    left_b = symbols.TypeAlias('LeftB', make_any())
    right_a = symbols.TypeAlias('RightA', make_any())
    right_b = symbols.TypeAlias('RightB', make_any())

    left_a_type = types.TypeAliasType(left_a, [])
    left_b_type = types.TypeAliasType(left_b, [])
    right_a_type = types.TypeAliasType(right_a, [])
    right_b_type = types.TypeAliasType(right_b, [])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(list_info, [left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(list_info, [right_a_type])

    assert is_structurally_equivalent(left_a_type, right_a_type)
    assert is_structurally_equivalent(left_a_type, left_a.target)
    assert is_structurally_equivalent(left_a.target, right_a.target)
    assert structural_type_key(left_a_type) == structural_type_key(right_a_type)
    assert structural_type_key(left_a_type) == structural_type_key(left_a.target)
    assert structural_type_key(left_a.target) == structural_type_key(right_a.target)


def test_structural_type_key_differs_when_recursive_alias_equivalence_differs() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([str_type, make_instance(list_info, [right_alias_type])])

    assert not is_structurally_equivalent(left_alias_type, right_alias_type)
    assert structural_type_key(left_alias_type) != structural_type_key(right_alias_type)


def test_structural_type_key_recursive_alias_matches_one_unrolling() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([int_type, make_instance(list_info, [alias_type])])

    assert structural_type_key(alias_type) == structural_type_key(alias.target)


def test_structural_type_key_recursive_alias_containing_type_type_matches_one_unrolling() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('ClassNode', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([
        types.TypeType(int_type),
        types.TypeType(make_instance(list_info, [alias_type])),
    ])
    unrolled = types.UnionType([
        types.TypeType(int_type),
        types.TypeType(make_instance(list_info, [alias.target])),
    ])

    assert structural_type_key(alias_type) == structural_type_key(alias.target)
    assert structural_type_key(alias_type) == structural_type_key(unrolled)


def test_structural_type_key_recursive_alias_matches_multiple_unrollings() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    one_unrolling = types.UnionType([int_type, make_instance(list_info, [alias_type])])
    two_unrollings = types.UnionType([int_type, make_instance(list_info, [one_unrolling])])
    alias._target = one_unrolling

    assert structural_type_key(alias_type) == structural_type_key(one_unrolling)
    assert structural_type_key(alias_type) == structural_type_key(two_unrollings)


def assert_same_structural_key_as_equivalent(left: types.Type, right: types.Type) -> None:
    assert is_structurally_equivalent(left, right)
    assert structural_type_key(left) == structural_type_key(right)


def assert_same_alpha_structural_key_as_equivalent(left: types.Type, right: types.Type) -> None:
    assert is_alpha_structurally_equivalent(left, right)
    assert alpha_structural_type_key(left) == alpha_structural_type_key(right)


def make_recursive_json_like_alias(
        name: str,
        *,
        reverse_union: bool = False,
        list_info: symbols.TypeInfo | None = None,
        dict_info: symbols.TypeInfo | None = None,
        bool_type: types.Instance | None = None,
        int_type: types.Instance | None = None,
        str_type: types.Instance | None = None,
) -> tuple[types.TypeAliasType, types.UnionType, types.UnionType]:
    if list_info is None:
        list_info = make_info('builtins.list')
    if dict_info is None:
        dict_info = make_info('builtins.dict')
    if bool_type is None:
        bool_type = make_instance(make_info('builtins.bool'))
    if int_type is None:
        int_type = make_instance(make_info('builtins.int'))
    if str_type is None:
        str_type = make_instance(make_info('builtins.str'))

    alias = symbols.TypeAlias(name, make_any())
    alias_type = types.TypeAliasType(alias, [])
    items: list[types.Type] = [
        types.NoneType(),
        bool_type,
        int_type,
        str_type,
        make_instance(list_info, [alias_type]),
        make_instance(dict_info, [str_type, alias_type]),
    ]
    if reverse_union:
        items.reverse()
    target = types.UnionType(items)
    alias._target = target
    unrolled = types.UnionType([
        types.NoneType(),
        bool_type,
        int_type,
        str_type,
        make_instance(list_info, [target]),
        make_instance(dict_info, [str_type, target]),
    ])
    return alias_type, target, unrolled


def test_structural_type_key_json_like_recursive_alias_is_cache_grade() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')
    bool_type = make_instance(make_info('builtins.bool'))
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    left_alias_type, left_target, left_unrolled = make_recursive_json_like_alias(
        'Jsonish',
        list_info=list_info,
        dict_info=dict_info,
        bool_type=bool_type,
        int_type=int_type,
        str_type=str_type,
    )
    right_alias_type, right_target, right_unrolled = make_recursive_json_like_alias(
        'OtherJsonish',
        reverse_union=True,
        list_info=list_info,
        dict_info=dict_info,
        bool_type=bool_type,
        int_type=int_type,
        str_type=str_type,
    )

    assert_same_structural_key_as_equivalent(left_alias_type, left_target)
    assert_same_structural_key_as_equivalent(left_alias_type, left_unrolled)
    assert_same_structural_key_as_equivalent(left_alias_type, right_alias_type)
    assert_same_structural_key_as_equivalent(left_target, right_target)
    assert_same_structural_key_as_equivalent(left_unrolled, right_unrolled)


def test_alpha_structural_type_key_recursive_alias_tracks_repeated_variable_positions() -> None:
    tuple_info = make_info('builtins.tuple')
    tuple_fallback = make_instance(tuple_info)
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)
    wrong_u = make_type_var('WrongU', 3)
    wrong_v = make_type_var('WrongV', 4)

    left_alias = symbols.TypeAlias('LeftPair', make_any(), alias_tvars=[left_t])
    right_alias = symbols.TypeAlias('RightPair', make_any(), alias_tvars=[right_u])
    wrong_alias = symbols.TypeAlias('WrongPair', make_any(), alias_tvars=[wrong_u, wrong_v])
    left_alias_type = types.TypeAliasType(left_alias, [left_t])
    right_alias_type = types.TypeAliasType(right_alias, [right_u])
    wrong_alias_type = types.TypeAliasType(wrong_alias, [wrong_u, wrong_v])

    left_alias._target = types.TupleType([left_t, left_t, left_alias_type], tuple_fallback)
    right_alias._target = types.TupleType([right_u, right_u, right_alias_type], tuple_fallback)
    wrong_alias._target = types.TupleType([wrong_u, wrong_v, wrong_alias_type], tuple_fallback)

    assert structural_type_key(left_alias_type) != structural_type_key(right_alias_type)
    assert_same_alpha_structural_key_as_equivalent(left_alias_type, right_alias_type)
    assert not is_alpha_structurally_equivalent(left_alias_type, wrong_alias_type)
    assert alpha_structural_type_key(left_alias_type) != alpha_structural_type_key(wrong_alias_type)


def test_structural_type_key_policy_knobs_for_recursive_metadata_are_independent() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('MetaNode', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([
        int_type,
        types.AnnotatedType(make_instance(list_info, [alias_type]), (('cfg', 1.5),)),
    ])
    reordered = types.UnionType([
        types.AnnotatedType(make_instance(list_info, [alias.target]), (('cfg', 1.5),)),
        int_type,
    ])
    policy = TypeKeyPolicy(
        structural=True,
        include_annotated_metadata=True,
        preserve_alias_identity=False,
    )

    assert structural_type_key(alias_type) == structural_type_key(reordered)
    assert type_key_with_policy_or_none(alias_type, policy) == type_key_with_policy_or_none(reordered, policy)
    assert type_key_with_policy_or_none(alias_type, policy) != structural_type_key(alias_type)


def test_structural_type_key_recursive_metadata_policy_fails_closed_for_unhashable_values() -> None:
    list_info = make_info('builtins.list')
    alias = symbols.TypeAlias('BadMetaNode', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.AnnotatedType(make_instance(list_info, [alias_type]), ([],))
    policy = TypeKeyPolicy(
        structural=True,
        include_annotated_metadata=True,
        preserve_alias_identity=False,
    )

    assert structural_type_key_or_none(alias_type) is not None
    assert type_key_with_policy_or_none(alias_type, policy) is None
    with pytest.raises(ReflectionError, match='not implemented'):
        type_key_with_policy(alias_type, policy)


def test_structural_type_key_recursive_alias_with_opaque_literals_is_union_order_insensitive() -> None:
    list_info = make_info('builtins.list')
    float_type = make_instance(make_info('builtins.float'))
    left_alias = symbols.TypeAlias('LeftFloatNode', make_any())
    right_alias = symbols.TypeAlias('RightFloatNode', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([
        types.LiteralType(1.5, float_type),
        types.LiteralType(2.5, float_type),
        make_instance(list_info, [left_alias_type]),
    ])
    right_alias._target = types.UnionType([
        make_instance(list_info, [right_alias_type]),
        types.LiteralType(2.5, float_type),
        types.LiteralType(1.5, float_type),
    ])
    left_unrolled = types.UnionType([
        make_instance(list_info, [left_alias.target]),
        types.LiteralType(2.5, float_type),
        types.LiteralType(1.5, float_type),
    ])

    assert_same_structural_key_as_equivalent(left_alias_type, right_alias_type)
    assert_same_structural_key_as_equivalent(left_alias_type, left_unrolled)


def test_structural_type_key_recursive_alias_with_callable_positions_matches_unrolling() -> None:
    callable_info = make_info('collections.abc.Callable')
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    alias = symbols.TypeAlias('FnNode', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([
        int_type,
        types.CallableType(
            [str_type, make_instance(list_info, [alias_type])],
            [symbols.ArgKind.POS, symbols.ArgKind.POS],
            [None, None],
            alias_type,
            make_instance(callable_info),
        ),
    ])
    unrolled = types.UnionType([
        int_type,
        types.CallableType(
            [str_type, make_instance(list_info, [alias.target])],
            [symbols.ArgKind.POS, symbols.ArgKind.POS],
            [None, None],
            alias.target,
            make_instance(callable_info),
        ),
    ])

    assert_same_structural_key_as_equivalent(alias_type, alias.target)
    assert_same_structural_key_as_equivalent(alias_type, unrolled)


def test_structural_type_key_recursive_alias_with_overload_matches_unrolling() -> None:
    callable_info = make_info('collections.abc.Callable')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    alias = symbols.TypeAlias('OverNode', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.Overloaded([
        types.CallableType([], [], [], int_type, make_instance(callable_info)),
        types.CallableType([str_type], [symbols.ArgKind.POS], [None], alias_type, make_instance(callable_info)),
    ])
    unrolled = types.Overloaded([
        types.CallableType([], [], [], int_type, make_instance(callable_info)),
        types.CallableType([str_type], [symbols.ArgKind.POS], [None], alias.target, make_instance(callable_info)),
    ])

    assert_same_structural_key_as_equivalent(alias_type, alias.target)
    assert_same_structural_key_as_equivalent(alias_type, unrolled)


def test_structural_type_key_recursive_alias_with_tuple_type_type_and_annotated_matches_unrolling() -> None:
    tuple_info = make_info('builtins.tuple')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('TupleNode', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.TupleType(
        [
            int_type,
            types.TypeType(types.AnnotatedType(alias_type, ('cfg',))),
        ],
        make_instance(tuple_info),
    )
    unrolled = types.TupleType(
        [
            int_type,
            types.TypeType(types.AnnotatedType(alias.target, ('different-cfg',))),
        ],
        make_instance(tuple_info),
    )

    assert_same_structural_key_as_equivalent(alias_type, alias.target)
    assert_same_structural_key_as_equivalent(alias_type, unrolled)


def test_structural_type_key_recursive_variadic_tuple_alias_matches_one_unrolling() -> None:
    case = make_recursive_variadic_tuple_alias_case('TupleNode', 1)

    assert_same_structural_key_as_equivalent(case.concrete_alias_type, case.one_unrolling)


def test_alpha_structural_type_key_recursive_variadic_tuple_aliases_match() -> None:
    left = make_recursive_variadic_tuple_alias_case('LeftTupleNode', 1)
    right = make_recursive_variadic_tuple_alias_case(
        'RightTupleNode',
        2,
        left.concrete_items,
        left.tuple_fallback,
    )

    assert structural_type_key(left.alias_type) != structural_type_key(right.alias_type)
    assert_same_alpha_structural_key_as_equivalent(left.alias_type, right.alias_type)


def test_structural_type_key_recursive_alias_preserves_newtype_leaf_identity() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    left_info = make_info('example.UserId')
    right_info = make_info('example.AccountId')
    left_info._new_type_supertype = int_type
    right_info._new_type_supertype = int_type
    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([make_instance(left_info), make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([make_instance(right_info), make_instance(list_info, [right_alias_type])])

    assert not is_structurally_equivalent(left_alias_type, right_alias_type)
    assert structural_type_key(left_alias_type) != structural_type_key(right_alias_type)


def test_alpha_structural_type_key_recursive_alias_with_reordered_union_and_type_vars() -> None:
    list_info = make_info('builtins.list')
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)
    left_alias = symbols.TypeAlias('Left', make_any(), alias_tvars=[left_t])
    right_alias = symbols.TypeAlias('Right', make_any(), alias_tvars=[right_u])
    left_alias_type = types.TypeAliasType(left_alias, [left_t])
    right_alias_type = types.TypeAliasType(right_alias, [right_u])
    left_alias._target = types.UnionType([left_t, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([make_instance(list_info, [right_alias_type]), right_u])

    assert structural_type_key(left_alias_type) != structural_type_key(right_alias_type)
    assert_same_alpha_structural_key_as_equivalent(left_alias_type, right_alias_type)


def test_structural_type_key_canonicalizes_nested_unrolled_recursive_alias() -> None:
    list_info = make_info('builtins.list')
    tuple_info = make_info('builtins.tuple')
    int_type = make_instance(make_info('builtins.int'))
    alias = symbols.TypeAlias('Node', make_any())
    alias_type = types.TypeAliasType(alias, [])
    one_unrolling = types.UnionType([int_type, make_instance(list_info, [alias_type])])
    two_unrollings = types.UnionType([int_type, make_instance(list_info, [one_unrolling])])
    alias._target = one_unrolling

    assert structural_type_key(make_instance(tuple_info, [alias_type])) == structural_type_key(
        make_instance(tuple_info, [two_unrollings]),
    )


def test_structural_type_key_unrolled_recursive_alias_still_compares_structure() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([str_type, make_instance(list_info, [right_alias_type])])

    assert structural_type_key(left_alias_type) == structural_type_key(left_alias.target)
    assert structural_type_key(right_alias_type) == structural_type_key(right_alias.target)
    assert structural_type_key(left_alias.target) != structural_type_key(right_alias.target)


def test_structural_type_key_multiple_recursive_alias_candidates_are_deterministic() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))

    left_alias = symbols.TypeAlias('Left', make_any())
    right_alias = symbols.TypeAlias('Right', make_any())
    left_alias_type = types.TypeAliasType(left_alias, [])
    right_alias_type = types.TypeAliasType(right_alias, [])
    left_alias._target = types.UnionType([int_type, make_instance(list_info, [left_alias_type])])
    right_alias._target = types.UnionType([str_type, make_instance(list_info, [right_alias_type])])

    both = types.UnionType([left_alias.target, right_alias.target])
    both_reordered = types.UnionType([right_alias.target, left_alias.target])
    left_only = types.UnionType([left_alias.target, str_type])

    assert structural_type_key(both) == structural_type_key(both_reordered)
    assert structural_type_key(both) != structural_type_key(left_only)


def test_alpha_structural_type_key_parameterized_recursive_alias_matches_one_unrolling() -> None:
    list_info = make_info('builtins.list')
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)

    left_alias = symbols.TypeAlias('Left', make_any(), alias_tvars=[left_t])
    right_alias = symbols.TypeAlias('Right', make_any(), alias_tvars=[right_u])
    left_alias_type = types.TypeAliasType(left_alias, [left_t])
    right_alias_type = types.TypeAliasType(right_alias, [right_u])
    left_alias._target = make_instance(list_info, [left_alias_type])
    right_alias._target = make_instance(list_info, [right_alias_type])

    assert alpha_structural_type_key(types.TypeAliasType(left_alias, [left_t])) == alpha_structural_type_key(
        right_alias.target,
    )


def test_alpha_structural_type_key_parameterized_mutual_recursion_canonicalizes_type_vars() -> None:
    list_info = make_info('builtins.list')
    dict_info = make_info('builtins.dict')

    left_t = make_type_var('T', 1)
    left_u = make_type_var('U', 2)
    right_x = make_type_var('X', 3)
    right_y = make_type_var('Y', 4)

    left_a = symbols.TypeAlias('LeftA', make_any(), alias_tvars=[left_t])
    left_b = symbols.TypeAlias('LeftB', make_any(), alias_tvars=[left_u])
    right_a = symbols.TypeAlias('RightA', make_any(), alias_tvars=[right_x])
    right_b = symbols.TypeAlias('RightB', make_any(), alias_tvars=[right_y])

    left_a_type = types.TypeAliasType(left_a, [left_t])
    left_b_type = types.TypeAliasType(left_b, [left_u])
    right_a_type = types.TypeAliasType(right_a, [right_x])
    right_b_type = types.TypeAliasType(right_b, [right_y])

    left_a._target = make_instance(list_info, [left_b_type])
    left_b._target = make_instance(dict_info, [left_u, left_a_type])
    right_a._target = make_instance(list_info, [right_b_type])
    right_b._target = make_instance(dict_info, [right_y, right_a_type])

    assert structural_type_key(types.TypeAliasType(left_a, [left_t])) != structural_type_key(
        types.TypeAliasType(right_a, [right_x]),
    )
    assert alpha_structural_type_key(types.TypeAliasType(left_a, [left_t])) == alpha_structural_type_key(
        types.TypeAliasType(right_a, [right_x]),
    )
    assert alpha_structural_type_key(types.TypeAliasType(left_b, [left_u])) == alpha_structural_type_key(
        types.TypeAliasType(right_b, [right_y]),
    )


def test_type_key_union_with_opaque_refs_uses_order_insensitive_bucket() -> None:
    tuple_type = make_instance(make_info('builtins.tuple'))
    left_value = (1.5,)
    right_value = (2.5,)
    left = types.UnionType([
        types.AnnotatedType(tuple_type, (left_value,)),
        types.AnnotatedType(tuple_type, (right_value,)),
    ])
    right = types.UnionType([
        types.AnnotatedType(tuple_type, (right_value,)),
        types.AnnotatedType(tuple_type, (left_value,)),
    ])
    opaque_bucket = frozenset({
        ("Ann[I['builtins.tuple'],$0]", (left_value,)),
        ("Ann[I['builtins.tuple'],$0]", (right_value,)),
    })

    assert type_key(left) == type_key(right)
    assert type_key(left) == ('U[OU[$0]]', opaque_bucket)


def test_type_key_single_opaque_ref_uses_ref_payload() -> None:
    tuple_type = make_instance(make_info('builtins.tuple'))
    value = (1.5,)

    assert type_key(types.AnnotatedType(tuple_type, (value,))) == ("Ann[I['builtins.tuple'],$0]", (value,))


def test_type_key_opaque_refs_use_value_equality() -> None:
    @dc.dataclass(frozen=True)
    class Token:
        value: int

    token_type = make_instance(make_info('example.Token'))
    left = types.AnnotatedType(token_type, (Token(1),))
    right = types.AnnotatedType(token_type, (Token(1),))
    different = types.AnnotatedType(token_type, (Token(2),))

    assert type_key(left) == type_key(right)
    assert type_key(left) != type_key(different)


def test_type_key_union_with_mixed_stringable_and_opaque_members_only_buckets_opaque_members() -> None:
    int_type = make_instance(make_info('builtins.int'))
    tuple_type = make_instance(make_info('builtins.tuple'))
    value = (1.5,)
    typ = types.UnionType([
        types.AnnotatedType(tuple_type, (value,)),
        types.LiteralType(1, int_type),
        types.NoneType(),
    ])

    assert type_key(typ) == (
        "U[L[int:1,I['builtins.int']],None,OU[$0]]",
        frozenset({("Ann[I['builtins.tuple'],$0]", (value,))}),
    )


def test_type_key_opaque_union_bucket_is_distinct_from_opaque_ref_value() -> None:
    tuple_type = make_instance(make_info('builtins.tuple'))
    frozenset_type = make_instance(make_info('builtins.frozenset'))
    value = (1.5,)
    child_key = type_key(types.AnnotatedType(tuple_type, (value,)))
    union = types.UnionType([types.AnnotatedType(tuple_type, (value,))])
    annotated_frozenset = types.AnnotatedType(frozenset_type, (frozenset({child_key}),))

    assert type_key(union) == ('U[OU[$0]]', frozenset({child_key}))
    assert type_key(annotated_frozenset) == ("Ann[I['builtins.frozenset'],$0]", (frozenset({child_key}),))
    assert type_key(union) != type_key(annotated_frozenset)


def test_type_key_unhashable_opaque_ref_fails_closed() -> None:
    typ = types.AnnotatedType(make_instance(make_info('list')), ([1],))

    assert type_key_or_none(typ) is None
    with pytest.raises(ReflectionError, match='not implemented'):
        type_key(typ)
    assert structural_type_key_or_none(typ) == "I['list']"
    assert alpha_structural_type_key_or_none(typ) == "I['list']"


def test_runtime_reflection_rejects_opaque_literal_values_before_literal_type_construction() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    with pytest.raises(ReflectionError, match='Unsupported literal value'):
        reflector.reflect_type(ta.Literal[frozenset({1})])


def test_alpha_type_key_recursive_alias_canonicalizes_type_vars() -> None:
    list_info = make_info('builtins.list')
    left_t = make_type_var('T', 1)
    right_u = make_type_var('U', 2)

    left_alias = symbols.TypeAlias('Left', make_any(), alias_tvars=[left_t])
    right_alias = symbols.TypeAlias('Right', make_any(), alias_tvars=[right_u])
    left_alias_type = types.TypeAliasType(left_alias, [left_t])
    right_alias_type = types.TypeAliasType(right_alias, [right_u])
    left_alias._target = make_instance(list_info, [left_alias_type])
    right_alias._target = make_instance(list_info, [right_alias_type])

    assert type_key(types.TypeAliasType(left_alias, [left_t])) != type_key(types.TypeAliasType(right_alias, [right_u]))
    assert alpha_type_key(types.TypeAliasType(left_alias, [left_t])) == alpha_type_key(
        types.TypeAliasType(right_alias, [right_u]),
    )


def test_type_key_returns_none_for_unsupported_nodes() -> None:
    assert type_key_or_none(types.PartialType(None, None)) is None
    assert alpha_type_key_or_none(types.PartialType(None, None)) is None
    assert structural_type_key_or_none(types.PartialType(None, None)) is None
    assert alpha_structural_type_key_or_none(types.PartialType(None, None)) is None
    with pytest.raises(ReflectionError, match='not implemented'):
        type_key(types.PartialType(None, None))
    with pytest.raises(ReflectionError, match='not implemented'):
        structural_type_key(types.PartialType(None, None))
    with pytest.raises(ReflectionError, match='not implemented'):
        alpha_structural_type_key(types.PartialType(None, None))


def test_structural_type_key_recursive_alias_with_unsupported_target_fails_closed() -> None:
    alias = symbols.TypeAlias('Bad', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([alias_type, types.PartialType(None, None)])

    assert alias_type.is_recursive
    assert structural_type_key_or_none(alias_type) is None
    assert alpha_structural_type_key_or_none(alias_type) is None
    with pytest.raises(ReflectionError, match='not implemented'):
        structural_type_key(alias_type)
    with pytest.raises(ReflectionError, match='not implemented'):
        alpha_structural_type_key(alias_type)


def test_structural_type_key_recursive_alias_with_bad_arg_count_fails_closed() -> None:
    list_info = make_info('builtins.list')
    int_type = make_instance(make_info('builtins.int'))
    str_type = make_instance(make_info('builtins.str'))
    t_var = make_type_var('T', 1)
    alias = symbols.TypeAlias('BadGeneric', make_any(), alias_tvars=[t_var])
    good_alias_type = types.TypeAliasType(alias, [t_var])
    bad_alias_type = types.TypeAliasType(alias, [int_type, str_type])
    alias._target = make_instance(list_info, [good_alias_type])

    assert bad_alias_type.is_recursive
    assert structural_type_key_or_none(bad_alias_type) is None
    assert alpha_structural_type_key_or_none(bad_alias_type) is None
    with pytest.raises(ReflectionError, match='not implemented'):
        structural_type_key(bad_alias_type)
    with pytest.raises(ReflectionError, match='not implemented'):
        alpha_structural_type_key(bad_alias_type)


def test_structural_type_key_unrolled_recursive_alias_with_unsupported_member_fails_closed() -> None:
    alias = symbols.TypeAlias('Bad', make_any())
    alias_type = types.TypeAliasType(alias, [])
    alias._target = types.UnionType([alias_type, types.PartialType(None, None)])
    unrolled = types.UnionType([alias_type, types.PartialType(None, None)])

    assert structural_type_key_or_none(unrolled) is None
    assert alpha_structural_type_key_or_none(unrolled) is None
    with pytest.raises(ReflectionError, match='not implemented'):
        structural_type_key(unrolled)
    with pytest.raises(ReflectionError, match='not implemented'):
        alpha_structural_type_key(unrolled)
