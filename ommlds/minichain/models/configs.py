from omlish import lang
from omlish import typedvalues as tv

from ..configs import Config


##


class ModelSpecifier(Config, tv.UniqueTypedValue, lang.Abstract):
    pass


class ModelName(tv.ScalarTypedValue[str], ModelSpecifier):
    pass


class ModelPath(tv.ScalarTypedValue[str], ModelSpecifier):
    pass
