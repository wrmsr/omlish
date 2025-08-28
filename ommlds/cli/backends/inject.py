import typing as ta

from omlish import inject as inj
from omlish import lang

from ...minichain.backends.catalogs.base import BackendCatalog
from ...minichain.backends.catalogs.strings import BackendStringBackendCatalog


##


def bind_strings_backends() -> inj.Elements:
    lst: list[inj.Elemental] = []

    lst.extend([
        inj.bind(BackendStringBackendCatalog, singleton=True),
        inj.bind(BackendCatalog, to_key=BackendStringBackendCatalog),
    ])

    from ...minichain.backends.impls.huggingface.repos import HuggingfaceModelRepoResolver
    from ...minichain.models.repos.resolving import ModelRepoResolver

    lst.extend([
        inj.bind(HuggingfaceModelRepoResolver, singleton=True),
        inj.bind(ModelRepoResolver, to_key=HuggingfaceModelRepoResolver),

    ])

    return inj.as_elements(*lst)


def bind_simple_backends() -> inj.Elements:
    lst: list[inj.Elemental] = []

    from ...minichain.backends.catalogs.simple import SimpleBackendCatalog
    from ...minichain.backends.catalogs.simple import SimpleBackendCatalogEntries
    from ...minichain.backends.catalogs.simple import SimpleBackendCatalogEntry

    lst.extend([
        inj.set_binder[SimpleBackendCatalogEntry](),
        inj.bind(
            lang.typed_lambda(SimpleBackendCatalogEntries, s=ta.AbstractSet[SimpleBackendCatalogEntry])(
                lambda s: list(s),
            ),
            singleton=True,
        ),
    ])

    lst.extend([
        inj.bind(SimpleBackendCatalog, singleton=True),
        inj.bind(BackendCatalog, to_key=SimpleBackendCatalog),
    ])

    from .standard import STANDARD_BACKEND_CATALOG_ENTRIES

    lst.extend([
        inj.bind_set_entry_const(ta.AbstractSet[SimpleBackendCatalogEntry], e)
        for e in STANDARD_BACKEND_CATALOG_ENTRIES
    ])

    return inj.as_elements(*lst)


def bind_backends(
        *,
        enable_backend_strings: bool = False,
) -> inj.Elements:
    lst: list[inj.Elemental] = []

    if enable_backend_strings:
        lst.append(bind_strings_backends())
    else:
        lst.append(bind_simple_backends())

    return inj.as_elements(*lst)
