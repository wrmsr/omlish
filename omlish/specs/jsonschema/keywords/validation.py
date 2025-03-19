from .... import lang
from .base import BooleanKeyword
from .base import KeywordsKeyword
from .base import KnownKeyword
from .base import NumberKeyword
from .base import StrOrStrsKeyword
from .base import StrToKeywordsKeyword


##


class ValidationKeyword(KnownKeyword, lang.Abstract, lang.Sealed):
    pass


##


class Type(StrOrStrsKeyword, ValidationKeyword, lang.Final, tag='type'):
    pass


class Items(KeywordsKeyword, ValidationKeyword, lang.Final, tag='items'):
    pass


class Required(StrOrStrsKeyword, ValidationKeyword, lang.Final, tag='required'):
    pass


class Properties(StrToKeywordsKeyword, ValidationKeyword, lang.Final, tag='properties'):
    pass


##


class MaxItems(NumberKeyword, ValidationKeyword, lang.Final, tag='maxItems'):
    pass


class MinItems(NumberKeyword, ValidationKeyword, lang.Final, tag='minItems'):
    pass


class UniqueItems(BooleanKeyword, ValidationKeyword, lang.Final, tag='uniqueItems'):
    pass


#


class Maximum(NumberKeyword, ValidationKeyword, lang.Final, tag='maximum'):
    pass


class ExclusiveMaximum(NumberKeyword, ValidationKeyword, lang.Final, tag='exclusiveMaximum'):
    pass


class Minimum(NumberKeyword, ValidationKeyword, lang.Final, tag='minimum'):
    pass


class ExclusiveMinimum(NumberKeyword, ValidationKeyword, lang.Final, tag='exclusiveMinimum'):
    pass
