import typing as ta


Value: ta.TypeAlias = ta.Union[  # noqa
    None,

    bool,
    int,
    float,
    # Number,
    str,
    bytes,

    list,  # list[Value],
    dict,  # dict[str, Value],

    # ta.Any,
]


##


VALUE_TYPES: tuple[type, ...] = (
    type(None),

    bool,
    int,
    float,
    str,
    bytes,

    list,
    dict,
)
