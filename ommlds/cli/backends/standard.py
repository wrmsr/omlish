import typing as ta

from ... import minichain as mc
from ...minichain.backends.catalogs.simple import SimpleBackendCatalogEntry
from ...minichain.backends.catalogs.simple import simple_backend_catalog_entry


##


STANDARD_BACKEND_CATALOG_ENTRIES: ta.Sequence[SimpleBackendCatalogEntry] = [
    simple_backend_catalog_entry(mc.ChatChoicesService, 'openai'),

    simple_backend_catalog_entry(mc.ChatChoicesStreamService, 'openai'),

    simple_backend_catalog_entry(mc.CompletionService, 'llamacpp'),
    simple_backend_catalog_entry(mc.CompletionService, 'openai'),
    simple_backend_catalog_entry(mc.CompletionService, 'tfm'),

    simple_backend_catalog_entry(mc.EmbeddingService, 'openai'),
    simple_backend_catalog_entry(mc.EmbeddingService, 'stfm'),
]
