from omlish import dataclasses as dc
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


@dc.dataclass(frozen=True)
class ModelRepo(ModelSpecifier):
    namespace: str
    repo: str

    _: dc.KW_ONLY

    tag: str | None = dc.xfield(None, repr_fn=dc.opt_repr)
    path: str | None = dc.xfield(None, repr_fn=dc.opt_repr)
