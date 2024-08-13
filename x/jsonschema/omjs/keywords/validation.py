from omlish import lang

from .base import BooleanKeyword
from .base import KeywordsKeyword
from .base import NumberKeyword
from .base import StrOrStrsKeyword
from .base import StrToKeywordsKeyword


##


class Type(StrOrStrsKeyword, lang.Final, tag='type'):
    pass


class Items(KeywordsKeyword, lang.Final, tag='items'):
    pass


class Required(StrOrStrsKeyword, lang.Final, tag='required'):
    pass


class Properties(StrToKeywordsKeyword, lang.Final, tag='properties'):
    pass


##


class MaxItems(NumberKeyword, lang.Final, tag='maxItems'):
    pass


class MinItems(NumberKeyword, lang.Final, tag='minItems'):
    pass


class UniqueItems(BooleanKeyword, lang.Final, tag='uniqueItems'):
    pass


#


class Maximum(NumberKeyword, lang.Final, tag='maximum'):
    pass


class ExclusiveMaximum(NumberKeyword, lang.Final, tag='exclusiveMaximum'):
    pass


class Minimum(NumberKeyword, lang.Final, tag='minimum'):
    pass


class ExclusiveMinimum(NumberKeyword, lang.Final, tag='exclusiveMinimum'):
    pass
