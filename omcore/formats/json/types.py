import typing as ta


Scalar: ta.TypeAlias = bool | int | float | str | None

SCALAR_TYPES: tuple[type, ...] = (bool, int, float, str, type(None))
