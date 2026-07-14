from .... import lang
from .base import KnownKeyword
from .base import StrKeyword


##


class FormatKeyword(KnownKeyword, lang.Abstract, lang.Sealed):
    pass


##


class Format(StrKeyword, FormatKeyword, lang.Final, tag='format'):
    pass
