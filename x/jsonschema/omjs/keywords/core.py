from omlish import lang

from .base import StrKeyword


##


class Id(StrKeyword, lang.Final, tag='$id'):
    pass


class SchemaKeyword(StrKeyword, lang.Final, tag='$schema'):
    pass


class Ref(StrKeyword, lang.Final, tag='$ref'):
    pass
