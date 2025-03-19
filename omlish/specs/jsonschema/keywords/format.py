from .... import lang
from .base import Keyword
from .base import StrKeyword


##


class FormatKeyword(Keyword, lang.Abstract, lang.Sealed):
    pass


##


class Format(StrKeyword, FormatKeyword, lang.Final, tag='format'):
    pass
