from .... import lang
from .base import KnownKeyword
from .base import StrKeyword


##


class MetadataKeyword(KnownKeyword, lang.Abstract, lang.Sealed):
    pass


##


class Title(StrKeyword, MetadataKeyword, lang.Final, tag='title'):
    pass


class Description(StrKeyword, MetadataKeyword, lang.Final, tag='description'):
    pass
