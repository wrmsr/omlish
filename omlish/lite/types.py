# ruff: noqa: UP006 UP007 UP045
import typing as ta


BUILTIN_SCALAR_ITERABLE_TYPES: ta.Tuple[type, ...] = (
    bytearray,
    bytes,
    str,
)
