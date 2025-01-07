import typing as ta


O = ta.TypeVar('O')
I = ta.TypeVar('I')
R = ta.TypeVar('R')


# Direct coros yield outputs 1:1 with inputs.
DirectCoro: ta.TypeAlias = ta.Generator[O, I, R]

BytesDirectCoro: ta.TypeAlias = DirectCoro[bytes, bytes, R]
StrDirectCoro: ta.TypeAlias = DirectCoro[str, str, R]
