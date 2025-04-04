from omlish import lang

from .options import Option
from .options import ScalarOption
from .options import UniqueOption


##


class Generative(lang.Abstract):
    pass


##


class GenerativeOption(Option, lang.Abstract):
    pass


class TopK(GenerativeOption, UniqueOption, ScalarOption[int], lang.Final):
    pass


class Temperature(GenerativeOption, UniqueOption, ScalarOption[float], lang.Final):
    pass


class MaxTokens(GenerativeOption, UniqueOption, ScalarOption[int], lang.Final):
    pass
