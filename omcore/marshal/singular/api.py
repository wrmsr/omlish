import typing as ta


##


PRIMITIVE_TYPES: ta.Final[tuple[type, ...]] = (
    type(None),

    bool,
    int,
    float,
    str,
    bytes,
)
