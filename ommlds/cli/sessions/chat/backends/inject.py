from omlish import inject as inj
from omlish import lang

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

    return inj.as_elements(*els)
