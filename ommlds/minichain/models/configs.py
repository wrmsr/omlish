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

    @property
    def slashed(self) -> str:
        return '/'.join([self.namespace, self.repo])

    @classmethod
    def parse(cls, s: str) -> 'ModelRepo':
        # FIXME: lol
        ns, r = s.split('/')
        return ModelRepo(ns, r)

    _: dc.KW_ONLY

    tag: str | None = dc.xfield(None, repr_fn=dc.opt_repr)
    path: str | None = dc.xfield(None, repr_fn=dc.opt_repr)
