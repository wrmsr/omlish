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
