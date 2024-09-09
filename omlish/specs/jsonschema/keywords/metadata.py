from omlish import lang

from .base import Keyword
from .base import StrKeyword


##


class MetadataKeyword(Keyword, lang.Abstract):
    pass


##


class Title(StrKeyword, MetadataKeyword, lang.Final, tag='title'):
    pass


class Description(StrKeyword, MetadataKeyword, lang.Final, tag='description'):
    pass
