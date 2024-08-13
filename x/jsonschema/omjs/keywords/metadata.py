from omlish import lang

from .base import StrKeyword


##


class Title(StrKeyword, lang.Final, tag='title'):
    pass


class Description(StrKeyword, lang.Final, tag='description'):
    pass
