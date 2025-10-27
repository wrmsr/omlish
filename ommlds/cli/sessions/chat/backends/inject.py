import typing as ta

from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from .injection import backend_configs


with lang.auto_proxy_import(globals()):
    from . import catalog as _catalog
    from . import types as _types


##


def bind_backends(
        *,
        backend: str | None = None,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(backend_configs().bind_items_provider(singleton=True))

    #

    if backend is not None:
        els.append(inj.bind(_types.BackendName, to_const=backend))

    els.extend([
        inj.bind(_types.ChatChoicesServiceBackendProvider, to_ctor=_catalog.CatalogChatChoicesServiceBackendProvider, singleton=True),  # noqa
        inj.bind(_types.ChatChoicesStreamServiceBackendProvider, to_ctor=_catalog.CatalogChatChoicesStreamServiceBackendProvider, singleton=True),  # noqa
    ])

    #

    async def catalog_backend_instantiator_provider(injector: inj.AsyncInjector) -> _catalog.CatalogBackendProvider.Instantiator:  # noqa
        async def inner(be: 'mc.BackendCatalog.Backend', cfgs: _types.BackendConfigs | None) -> ta.Any:
            raise NotImplementedError

        return _catalog.CatalogBackendProvider.Instantiator(inner)

    els.append(inj.bind(_catalog.CatalogBackendProvider.Instantiator, to_async_fn=catalog_backend_instantiator_provider))  # noqa

    #

    return inj.as_elements(*els)
