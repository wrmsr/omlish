from omlish import lang

from .options import Option
from .options import ScalarOption
from .options import UniqueOption


##


class Generative(lang.Abstract):
    pass


##


class GenerativeRequestOption(Option, lang.Abstract):
    pass


class TopK(GenerativeRequestOption, UniqueOption, ScalarOption[int], lang.Final):
    pass


class Temperature(GenerativeRequestOption, UniqueOption, ScalarOption[float], lang.Final):
    pass


class MaxTokens(GenerativeRequestOption, UniqueOption, ScalarOption[int], lang.Final):
    pass
