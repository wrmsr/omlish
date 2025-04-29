from .... import lang
from .base import AnyArrayKeyword
from .base import AnyKeyword
from .base import BooleanKeyword
from .base import BooleanOrKeywordsKeyword
from .base import KeywordsArrayKeyword
from .base import KeywordsKeyword
from .base import KnownKeyword
from .base import NumberKeyword
from .base import StrOrStrArrayKeyword
from .base import StrToKeywordsKeyword


##


class ValidationKeyword(KnownKeyword, lang.Abstract, lang.Sealed):
    pass


##


class Type(StrOrStrArrayKeyword, ValidationKeyword, lang.Final, tag='type'):
    pass


class Const(AnyKeyword, ValidationKeyword, lang.Final, tag='const'):
    pass


class Enum(AnyArrayKeyword, ValidationKeyword, lang.Final, tag='enum'):
    pass


class Items(KeywordsKeyword, ValidationKeyword, lang.Final, tag='items'):
    pass


class Required(StrOrStrArrayKeyword, ValidationKeyword, lang.Final, tag='required'):
    pass


class Properties(StrToKeywordsKeyword, ValidationKeyword, lang.Final, tag='properties'):
    pass


class AdditionalProperties(BooleanOrKeywordsKeyword, ValidationKeyword, lang.Final, tag='additionalProperties'):
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


#


class AnyOf(KeywordsArrayKeyword, ValidationKeyword, lang.Final, tag='anyOf'):
    pass


class OneOf(KeywordsArrayKeyword, ValidationKeyword, lang.Final, tag='oneOf'):
    pass
