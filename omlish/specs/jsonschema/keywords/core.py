from .... import lang
from .base import KnownKeyword
from .base import StrKeyword
from .base import StrToKeywordsKeyword


##


class CoreKeyword(KnownKeyword, lang.Abstract, lang.Sealed):
    pass


##


class Id(StrKeyword, CoreKeyword, lang.Final, tag='$id'):
    pass


class SchemaKeyword(StrKeyword, CoreKeyword, lang.Final, tag='$schema'):
    pass


class Ref(StrKeyword, CoreKeyword, lang.Final, tag='$ref'):
    pass


class Defs(StrToKeywordsKeyword, CoreKeyword, lang.Final, tag='$defs', aliases=['definitions']):
    pass
