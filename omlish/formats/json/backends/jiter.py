"""
from_json(
    json_data: bytes,
    /,
    *,
    allow_inf_nan: bool = True,
    cache_mode: Literal[True, False, "all", "keys", "none"] = "all",
    partial_mode: Literal[True, False, "off", "on", "trailing-strings"] = False,
    catch_duplicate_keys: bool = False,
    lossless_floats: bool = False,
) -> Any:
    json_data: The JSON data to parse
    allow_inf_nan: Whether to allow infinity (`Infinity` an `-Infinity`) and `NaN` values to float fields.
    Defaults to True.
    cache_mode: cache Python strings to improve performance at the cost of some memory usage
    - True / 'all' - cache all strings
    - 'keys' - cache only object keys
    - False / 'none' - cache nothing
    partial_mode: How to handle incomplete strings:
    - False / 'off' - raise an exception if the input is incomplete
    - True / 'on' - allow incomplete JSON but discard the last string if it is incomplete
    - 'trailing-strings' - allow incomplete JSON, and include the last incomplete string in the output
    catch_duplicate_keys: if True, raise an exception if objects contain the same key multiple times
    lossless_floats: if True, preserve full detail on floats using `LosslessFloat`
"""
