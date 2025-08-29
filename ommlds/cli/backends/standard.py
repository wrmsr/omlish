import typing as ta

from ... import minichain as mc


##


STANDARD_BACKEND_CATALOG_ENTRIES: ta.Sequence[mc.SimpleBackendCatalogEntry] = [
    mc.simple_backend_catalog_entry(mc.ChatChoicesService, 'openai'),

    mc.simple_backend_catalog_entry(mc.ChatChoicesStreamService, 'openai'),

    mc.simple_backend_catalog_entry(mc.CompletionService, 'llamacpp'),
    mc.simple_backend_catalog_entry(mc.CompletionService, 'openai'),
    mc.simple_backend_catalog_entry(mc.CompletionService, 'tfm'),

    mc.simple_backend_catalog_entry(mc.EmbeddingService, 'openai'),
    mc.simple_backend_catalog_entry(mc.EmbeddingService, 'stfm'),
]
