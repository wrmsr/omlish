# import abc
# import typing as ta
#
# from omlish import collections as col
# from omlish import dataclasses as dc
# from omlish import dataclasses as lang
# from omlish.manifests.globals import GlobalManifestLoader
#
# from ..types import BackendSpec
# from ....registries.globals import get_global_registry
# from ...strings.manifests import BackendStringsManifest
# from ..types import NameBackendSpec
# from ....chat.choices.services import ChatChoicesService
#
#
# ##
#
#
# @dc.dataclass(frozen=True)
# class ResolvedBackendSpec:
#     service_cls: ta.Any
#     spec: BackendSpec
#     ctor: ta.Callable[..., ta.Any]
#
#
# def resolve_backend_spec(service_cls: ta.Any, spec: BackendSpec) -> ResolvedBackendSpec:
#     rt = get_global_registry().get_registered_type(service_cls)
#     scn_set = rt.names or frozenset()
#     bsm_lst: list[BackendStringsManifest] = [
#         bsm
#         for bsm in GlobalManifestLoader.load_values_of(BackendStringsManifest)
#         if any(scn in scn_set for scn in bsm.service_cls_names)
#     ]
#     raise NotImplementedError
#
#
# ##
#
#
# def test_strings():
#     print(resolve_backend_spec(ChatChoicesService, NameBackendSpec('openai')))
