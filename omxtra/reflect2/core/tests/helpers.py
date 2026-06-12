# ruff: noqa: SLF001
from .. import symbols
from .. import types


class RecursiveVariadicTupleAliasCase:
    __slots__ = (
        'alias',
        'alias_type',
        'concrete_alias_type',
        'concrete_items',
        'one_unrolling',
        'packed_concrete_arg',
        'packed_generic_arg',
        'tuple_fallback',
        'type_var_tuple',
    )

    def __init__(
            self,
            alias: symbols.TypeAlias,
            alias_type: types.TypeAliasType,
            concrete_alias_type: types.TypeAliasType,
            concrete_items: list[types.Type],
            one_unrolling: types.TupleType,
            packed_concrete_arg: types.TupleType,
            packed_generic_arg: types.TupleType,
            tuple_fallback: types.Instance,
            type_var_tuple: types.TypeVarTupleType,
    ) -> None:
        super().__init__()

        self.alias = alias
        self.alias_type = alias_type
        self.concrete_alias_type = concrete_alias_type
        self.concrete_items = concrete_items
        self.one_unrolling = one_unrolling
        self.packed_concrete_arg = packed_concrete_arg
        self.packed_generic_arg = packed_generic_arg
        self.tuple_fallback = tuple_fallback
        self.type_var_tuple = type_var_tuple


class RecursiveJsonLikeAliasCase:
    __slots__ = (
        'alias',
        'alias_type',
        'bool_type',
        'dict_info',
        'int_type',
        'list_info',
        'one_unrolling',
        'str_type',
        'target',
    )

    def __init__(
            self,
            alias: symbols.TypeAlias,
            alias_type: types.TypeAliasType,
            bool_type: types.Instance,
            dict_info: symbols.TypeInfo,
            int_type: types.Instance,
            list_info: symbols.TypeInfo,
            one_unrolling: types.UnionType,
            str_type: types.Instance,
            target: types.UnionType,
    ) -> None:
        super().__init__()

        self.alias = alias
        self.alias_type = alias_type
        self.bool_type = bool_type
        self.dict_info = dict_info
        self.int_type = int_type
        self.list_info = list_info
        self.one_unrolling = one_unrolling
        self.str_type = str_type
        self.target = target


class RecursiveMixedTupleAliasCase:
    __slots__ = (
        'alias',
        'alias_type',
        'concrete_alias_type',
        'concrete_type_var_item',
        'concrete_type_var_tuple_items',
        'one_unrolling',
        'packed_concrete_arg',
        'packed_generic_arg',
        'tuple_fallback',
        'type_var',
        'type_var_tuple',
    )

    def __init__(
            self,
            alias: symbols.TypeAlias,
            alias_type: types.TypeAliasType,
            concrete_alias_type: types.TypeAliasType,
            concrete_type_var_item: types.Type,
            concrete_type_var_tuple_items: list[types.Type],
            one_unrolling: types.TupleType,
            packed_concrete_arg: types.TupleType,
            packed_generic_arg: types.TupleType,
            tuple_fallback: types.Instance,
            type_var: types.TypeVarType,
            type_var_tuple: types.TypeVarTupleType,
    ) -> None:
        super().__init__()

        self.alias = alias
        self.alias_type = alias_type
        self.concrete_alias_type = concrete_alias_type
        self.concrete_type_var_item = concrete_type_var_item
        self.concrete_type_var_tuple_items = concrete_type_var_tuple_items
        self.one_unrolling = one_unrolling
        self.packed_concrete_arg = packed_concrete_arg
        self.packed_generic_arg = packed_generic_arg
        self.tuple_fallback = tuple_fallback
        self.type_var = type_var
        self.type_var_tuple = type_var_tuple


def make_any() -> types.AnyType:
    return types.AnyType(types.TypeOfAny.EXPLICIT)


def make_info(name: str) -> symbols.TypeInfo:
    return symbols.TypeInfo(name, name)


def make_instance(info: symbols.TypeInfo, args: list[types.Type] | None = None) -> types.Instance:
    return types.Instance(info, [] if args is None else args)


def make_type_var(name: str, raw_id: int) -> types.TypeVarType:
    any_type = make_any()
    return types.TypeVarType(
        name,
        name,
        types.TypeVarId(raw_id),
        [],
        any_type,
        any_type,
    )


def make_type_var_tuple(name: str, raw_id: int) -> types.TypeVarTupleType:
    any_type = make_any()
    tuple_fallback = make_instance(make_info('builtins.tuple'), [any_type])
    return types.TypeVarTupleType(
        name,
        name,
        types.TypeVarId(raw_id),
        any_type,
        any_type,
        tuple_fallback,
    )


def make_recursive_variadic_tuple_alias_case(
        name: str,
        raw_id: int,
        concrete_items: list[types.Type] | None = None,
        tuple_fallback: types.Instance | None = None,
) -> RecursiveVariadicTupleAliasCase:
    if tuple_fallback is None:
        tuple_fallback = make_instance(make_info('builtins.tuple'), [make_any()])

    type_var_tuple = types.TypeVarTupleType(
        f'{name}Ts',
        f'{name}Ts',
        types.TypeVarId(raw_id),
        make_any(),
        make_any(),
        tuple_fallback,
    )
    alias = symbols.TypeAlias(name, make_any(), alias_tvars=[type_var_tuple])
    packed_generic_arg = types.TupleType([types.UnpackType(type_var_tuple)], tuple_fallback)
    alias_type = types.TypeAliasType(alias, [packed_generic_arg])
    alias._target = types.TupleType(
        [
            types.UnpackType(type_var_tuple),
            alias_type,
        ],
        tuple_fallback,
    )

    if concrete_items is None:
        concrete_items = [
            make_instance(make_info('builtins.int')),
            make_instance(make_info('builtins.str')),
        ]

    packed_concrete_arg = types.TupleType(concrete_items, tuple_fallback)
    concrete_alias_type = types.TypeAliasType(alias, [packed_concrete_arg])
    one_unrolling = types.TupleType([*concrete_items, concrete_alias_type], tuple_fallback)

    return RecursiveVariadicTupleAliasCase(
        alias,
        alias_type,
        concrete_alias_type,
        concrete_items,
        one_unrolling,
        packed_concrete_arg,
        packed_generic_arg,
        tuple_fallback,
        type_var_tuple,
    )


def make_recursive_json_like_alias_case(
        name: str,
        *,
        reverse_union: bool = False,
        list_info: symbols.TypeInfo | None = None,
        dict_info: symbols.TypeInfo | None = None,
        bool_type: types.Instance | None = None,
        int_type: types.Instance | None = None,
        str_type: types.Instance | None = None,
) -> RecursiveJsonLikeAliasCase:
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
    one_unrolling = types.UnionType([
        types.NoneType(),
        bool_type,
        int_type,
        str_type,
        make_instance(list_info, [target]),
        make_instance(dict_info, [str_type, target]),
    ])

    return RecursiveJsonLikeAliasCase(
        alias,
        alias_type,
        bool_type,
        dict_info,
        int_type,
        list_info,
        one_unrolling,
        str_type,
        target,
    )


def make_recursive_mixed_tuple_alias_case(
        name: str,
        type_var_raw_id: int,
        type_var_tuple_raw_id: int,
        concrete_type_var_item: types.Type | None = None,
        concrete_type_var_tuple_items: list[types.Type] | None = None,
        tuple_fallback: types.Instance | None = None,
) -> RecursiveMixedTupleAliasCase:
    if tuple_fallback is None:
        tuple_fallback = make_instance(make_info('builtins.tuple'), [make_any()])
    if concrete_type_var_item is None:
        concrete_type_var_item = make_instance(make_info('builtins.str'))
    if concrete_type_var_tuple_items is None:
        concrete_type_var_tuple_items = [
            make_instance(make_info('builtins.int')),
            make_instance(make_info('builtins.bool')),
        ]

    type_var = make_type_var(f'{name}T', type_var_raw_id)
    type_var_tuple = types.TypeVarTupleType(
        f'{name}Ts',
        f'{name}Ts',
        types.TypeVarId(type_var_tuple_raw_id),
        make_any(),
        make_any(),
        tuple_fallback,
    )
    alias = symbols.TypeAlias(name, make_any(), alias_tvars=[type_var, type_var_tuple])
    packed_generic_arg = types.TupleType([types.UnpackType(type_var_tuple)], tuple_fallback)
    alias_type = types.TypeAliasType(alias, [type_var, packed_generic_arg])
    alias._target = types.TupleType(
        [
            type_var,
            types.UnpackType(type_var_tuple),
            alias_type,
        ],
        tuple_fallback,
    )

    packed_concrete_arg = types.TupleType(concrete_type_var_tuple_items, tuple_fallback)
    concrete_alias_type = types.TypeAliasType(alias, [concrete_type_var_item, packed_concrete_arg])
    one_unrolling = types.TupleType(
        [
            concrete_type_var_item,
            *concrete_type_var_tuple_items,
            concrete_alias_type,
        ],
        tuple_fallback,
    )

    return RecursiveMixedTupleAliasCase(
        alias,
        alias_type,
        concrete_alias_type,
        concrete_type_var_item,
        concrete_type_var_tuple_items,
        one_unrolling,
        packed_concrete_arg,
        packed_generic_arg,
        tuple_fallback,
        type_var,
        type_var_tuple,
    )


def make_typed_dict(
        items: dict[str, types.Type],
        required_keys: set[str],
        readonly_keys: set[str] | None = None,
) -> types.TypedDictType:
    return types.TypedDictType(
        items,
        required_keys,
        set() if readonly_keys is None else readonly_keys,
        make_instance(make_info('dict'), [make_instance(make_info('str')), make_instance(make_info('object'))]),
    )
