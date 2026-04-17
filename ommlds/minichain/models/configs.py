from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv

from ..configs import Config


##


class ModelSpecifier(Config, tv.UniqueTypedValue, lang.Sealed, lang.Abstract):
    pass


class ModelName(tv.ScalarTypedValue[str], ModelSpecifier):
    pass


class ModelPath(tv.ScalarTypedValue[str], ModelSpecifier):
    pass


@dc.dataclass(frozen=True)
@msh.update_fields_options(['tag', 'path'], omit_if=lang.is_none)
class ModelRepo(ModelSpecifier):
    namespace: str
    repo: str

    @property
    def slashed(self) -> str:
        return '/'.join([self.namespace, self.repo])

    @classmethod
    def parse(cls, s: str) -> ModelRepo:
        # FIXME: lol
        ns, r = s.split('/')
        return ModelRepo(ns, r)

    _: dc.KW_ONLY

    tag: str | None = dc.xfield(None, repr_fn=lang.opt_repr)
    path: str | None = dc.xfield(None, repr_fn=lang.opt_repr)


##


@msh.register_global_lazy_init
def _configure_marshal(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories_to(cfgs, *msh.standard_polymorphism_factories(
        msh.Polymorphism(
            ModelSpecifier,
            [
                msh.Impl(ModelName, 'name'),
                msh.Impl(ModelPath, 'path'),
                msh.Impl(ModelRepo, 'repo'),
            ],
        ),
    ))
