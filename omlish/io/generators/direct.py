import typing as ta


O = ta.TypeVar('O')
I = ta.TypeVar('I')
R = ta.TypeVar('R')


# Direct generators yield outputs 1:1 with inputs.
DirectGenerator: ta.TypeAlias = ta.Generator[O, I, R]

BytesDirectGenerator: ta.TypeAlias = DirectGenerator[bytes, bytes, R]
StrDirectGenerator: ta.TypeAlias = DirectGenerator[str, str, R]
