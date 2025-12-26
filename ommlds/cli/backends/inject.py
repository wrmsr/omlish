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
    from . import meta as _meta
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
    else:
        lst.append(inj.bind(_types.BackendName, to_fn=inj.target(dbn=_types.DefaultBackendName)(lambda dbn: dbn)))

    backend_provider_pairs: list = [
        (_types.ChatChoicesServiceBackendProvider, _catalog.CatalogChatChoicesServiceBackendProvider),
        (_types.ChatChoicesStreamServiceBackendProvider, _catalog.CatalogChatChoicesStreamServiceBackendProvider),
        (_types.CompletionServiceBackendProvider, _catalog.CatalogCompletionServiceBackendProvider),
        (_types.EmbeddingServiceBackendProvider, _catalog.CatalogEmbeddingServiceBackendProvider),
    ]

    for bp_iface, bp_impl in backend_provider_pairs:
        bp_stack = inj.wrapper_binder_helper(bp_iface)

        if bp_iface is _types.ChatChoicesServiceBackendProvider:
            fiw_ben_lst: list[str] = [
                # 'openai',
                # 'anthropic',
                # 'groq',
                # 'cerebras',
            ]

            if fiw_ben_lst:
                for ben in fiw_ben_lst:
                    ben_bp_key: inj.Key = inj.Key(bp_impl, tag=ben)
                    lst.extend([
                        inj.private(
                            inj.bind(_types.BackendName, to_const=ben),
                            inj.bind(ben_bp_key, to_ctor=bp_impl, singleton=True, expose=True),
                            inj.bind(bp_iface, to_key=ben_bp_key),
                        ),
                        bp_stack.push_bind(to_key=ben_bp_key),
                    ])

                fiw_key: inj.Key = inj.Key(_meta.FirstInWinsBackendProvider, tag=bp_iface)
                lst.extend([
                    inj.private(
                        inj.set_binder[_types.BackendProvider]().bind(bp_stack.top),
                        inj.bind(fiw_key, to_ctor=_meta.FirstInWinsBackendProvider, singleton=True, expose=True),
                    ),
                    bp_stack.push_bind(to_key=fiw_key),
                ])

            else:
                lst.append(bp_stack.push_bind(to_ctor=bp_impl, singleton=True))

        else:
            lst.append(bp_stack.push_bind(to_ctor=bp_impl, singleton=True))

        lst.append(inj.bind(bp_iface, to_key=bp_stack.top))

    #

    async def catalog_backend_instantiator_provider(injector: inj.AsyncInjector) -> _catalog.CatalogBackendProvider.Instantiator:  # noqa
        async def inner(be: 'mc.BackendCatalog.Backend', cfgs: _types.BackendConfigs | None) -> ta.Any:
            kwt = inj.build_kwargs_target(be.factory, non_strict=True)
            kw = await injector.provide_kwargs(kwt)
            return be.factory(*tv.collect(*(be.configs or []), *(cfgs or []), override=True), **kw)

        return _catalog.CatalogBackendProvider.Instantiator(inner)

    lst.append(inj.bind(_catalog.CatalogBackendProvider.Instantiator, to_async_fn=catalog_backend_instantiator_provider))  # noqa

    return inj.as_elements(*lst)
