import typing as ta


##


LITERAL_UNION_TYPES: ta.Final[tuple[type, ...]] = (
    int,
    str,
)


##


PRIMITIVE_UNION_TYPES: ta.Final[tuple[type, ...]] = (
    float,
    int,
    str,
    bool,
)
