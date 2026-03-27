import typing as ta


# Snapshots may hold `_AutoKey`'s, but otherwise hold pure unwrapped values.
Snap: ta.TypeAlias = dict[str, ta.Any]
