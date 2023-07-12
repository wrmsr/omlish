"""
Null
Bool
Int
Float
Number
String
Bytes
Array
Object
Any
"""
import typing as ta


Value = ta.Union[
    None,
    bool,
    int,
    float,
    # Number,
    str,
    bytes,
    list,  # ta.Sequence[Value],
    dict,  # ta.Mapping[str, Value],
    # ta.Any,
]
