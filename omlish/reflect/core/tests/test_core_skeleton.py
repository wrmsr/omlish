from .. import types


EXPECTED_TYPE_CLASSES = [
    'Type',
    'TypeAliasType',
    'TypeGuardedType',
    'AnnotatedType',
    'RequiredType',
    'ReadOnlyType',
    'ProperType',
    'TypeVarLikeType',
    'TypeVarType',
    'ParamSpecType',
    'TypeVarTupleType',
    'UnboundType',
    'CallableArgument',
    'TypeList',
    'UnpackType',
    'AnyType',
    'UninhabitedType',
    'NoneType',
    'ErasedType',
    'DeletedType',
    'Instance',
    'FunctionLike',
    'Parameters',
    'CallableType',
    'Overloaded',
    'TupleType',
    'TypedDictType',
    'RawExpressionType',
    'LiteralType',
    'UnionType',
    'PartialType',
    'EllipsisType',
    'TypeType',
    'PlaceholderType',
    '_TestingUnknownType',
]


def test_type_hierarchy_class_list() -> None:
    for name in EXPECTED_TYPE_CLASSES:
        assert isinstance(getattr(types, name), type)


def test_type_hierarchy_matches_mypy_2_1_0_core_list() -> None:
    actual = [
        name
        for name, obj in vars(types).items()
        if isinstance(obj, type)
        and issubclass(obj, types.Type)
        and obj.__module__ == types.__name__
    ]

    assert actual == EXPECTED_TYPE_CLASSES
