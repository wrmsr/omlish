import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


NonSpecialToken = ta.NewType('NonSpecialToken', int)


class SpecialToken(int):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({int(self)})'


Token: ta.TypeAlias = SpecialToken | NonSpecialToken

TokenT = ta.TypeVar('TokenT', bound=Token)


#


def cast_token(i: int) -> Token:
    return ta.cast(Token, i)


def check_token(i: TokenT) -> TokenT:
    if (ic := i.__class__) is not int and ic is not NonSpecialToken:
        raise TypeError(i)
    return i


##


class TokenStr(dc.Box[str], lang.Final):
    pass
