import typing as ta

from omlish import inject as inj
from omlish import lang

from ... import minichain as mc


##


def bind_strings_backends() -> inj.Elements:
    lst: list[inj.Elemental] = []

    lst.extend([
        inj.bind(mc.BackendStringBackendCatalog, singleton=True),
        inj.bind(mc.BackendCatalog, to_key=mc.BackendStringBackendCatalog),
    ])

    from ...minichain.backends.impls.huggingface.repos import HuggingfaceModelRepoResolver

    lst.extend([
        inj.bind(HuggingfaceModelRepoResolver, singleton=True),
        inj.bind(mc.ModelRepoResolver, to_key=HuggingfaceModelRepoResolver),

    ])

    return inj.as_elements(*lst)


def bind_simple_backends() -> inj.Elements:
    lst: list[inj.Elemental] = []

    lst.extend([
        inj.set_binder[mc.SimpleBackendCatalogEntry](),
        inj.bind(
            lang.typed_lambda(mc.SimpleBackendCatalogEntries, s=ta.AbstractSet[mc.SimpleBackendCatalogEntry])(
                lambda s: list(s),
            ),
            singleton=True,
        ),
    ])

    lst.extend([
        inj.bind(mc.SimpleBackendCatalog, singleton=True),
        inj.bind(mc.BackendCatalog, to_key=mc.SimpleBackendCatalog),
    ])

    from .standard import STANDARD_BACKEND_CATALOG_ENTRIES

    lst.extend([
        inj.bind_set_entry_const(ta.AbstractSet[mc.SimpleBackendCatalogEntry], e)
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
