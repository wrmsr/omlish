from .... import lang
from .base import BooleanKeyword
from .base import Keyword
from .base import KeywordsKeyword
from .base import NumberKeyword
from .base import StrOrStrsKeyword
from .base import StrToKeywordsKeyword


##


class ValidationKeyword(Keyword, lang.Abstract, lang.Sealed):
    pass


