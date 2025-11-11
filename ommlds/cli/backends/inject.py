import typing as ta

from omlish import inject as inj
from omlish import lang
from omlish import typedvalues as tv

from ... import minichain as mc
from .configs import BackendConfig
from .injection import backend_configs


with lang.auto_proxy_import(globals()):
    from ...minichain.backends.impls.huggingface import repos as hf_repos
    from . import catalog as _catalog
    from . import types as _types


##


def bind_backends(cfg: BackendConfig = BackendConfig()) -> inj.Elements:
    lst: list[inj.Elemental] = []

    #

    lst.extend([
        inj.bind(mc.BackendStringBackendCatalog, singleton=True),
        inj.bind(mc.BackendCatalog, to_key=mc.BackendStringBackendCatalog),
    ])

    lst.extend([
        inj.bind(hf_repos.HuggingfaceModelRepoResolver, singleton=True),
        inj.bind(mc.ModelRepoResolver, to_key=hf_repos.HuggingfaceModelRepoResolver),

    ])

    #

    lst.append(backend_configs().bind_items_provider(singleton=True))

    #

    if cfg.backend is not None:
        lst.append(inj.bind(_types.BackendName, to_const=cfg.backend))

    lst.extend([
        inj.bind(_types.ChatChoicesServiceBackendProvider, to_ctor=_catalog.CatalogChatChoicesServiceBackendProvider, singleton=True),  # noqa
        inj.bind(_types.ChatChoicesStreamServiceBackendProvider, to_ctor=_catalog.CatalogChatChoicesStreamServiceBackendProvider, singleton=True),  # noqa
        inj.bind(_types.CompletionServiceBackendProvider, to_ctor=_catalog.CatalogCompletionServiceBackendProvider, singleton=True),  # noqa
        inj.bind(_types.EmbeddingServiceBackendProvider, to_ctor=_catalog.CatalogEmbeddingServiceBackendProvider, singleton=True),  # noqa
    ])

    #

    async def catalog_backend_instantiator_provider(injector: inj.AsyncInjector) -> _catalog.CatalogBackendProvider.Instantiator:  # noqa
        async def inner(be: 'mc.BackendCatalog.Backend', cfgs: _types.BackendConfigs | None) -> ta.Any:
            kwt = inj.build_kwargs_target(be.factory, non_strict=True)
            kw = await injector.provide_kwargs(kwt)
            return be.factory(*tv.collect(*(be.configs or []), *(cfgs or []), override=True), **kw)

        return _catalog.CatalogBackendProvider.Instantiator(inner)

    lst.append(inj.bind(_catalog.CatalogBackendProvider.Instantiator, to_async_fn=catalog_backend_instantiator_provider))  # noqa

    return inj.as_elements(*lst)
