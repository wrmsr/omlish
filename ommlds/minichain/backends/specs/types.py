"""
TODO:
 - configs?? unmarshaling depends on service_cls
"""
import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json5

from ...models.configs import ModelSpecifier


##


CanBackendSpec: ta.TypeAlias = ta.Union[
    str,
    'BackendSpec',
]


@dc.dataclass(frozen=True)
class BackendSpec(lang.Sealed):
    @ta.final
    @classmethod
    def of(cls, obj: CanBackendSpec) -> BackendSpec:
        check.is_(cls, BackendSpec, 'Must not access `BackendSpec.of()` through a subclass.')

        if isinstance(obj, BackendSpec):
            return obj

        elif isinstance(obj, str):
            return msh.unmarshal(json5.loads(obj), BackendSpec)

        else:
            raise TypeError(obj)


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True)
class NameBackendSpec(BackendSpec, lang.Final):
    name: str


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True)
class ModelBackendSpec(BackendSpec, lang.Final):
    model: ModelSpecifier


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True)
class RetryBackendSpec(BackendSpec, lang.Final):
    child: CanBackendSpec


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True)
class FirstInWinsBackendSpec(BackendSpec, lang.Final):
    children: ta.Sequence[CanBackendSpec]


#


@msh.register_global_lazy_init
def _setup_backend_spec_marshal(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories_to(cfgs, *msh.standard_polymorphism_factories(
        msh.polymorphism_from_subclasses(
            BackendSpec,
            strip_suffix=True,
            naming=msh.Naming.SNAKE,
        ),
    ))


##


@dc.dataclass(frozen=True)
class ResolvedBackendSpec(lang.Final):
    service_cls: ta.Any
    spec: BackendSpec


class BackendSpecResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve_backend_spec(self, service_cls: ta.Any, spec: BackendSpec) -> ResolvedBackendSpec:
        raise NotImplementedError
