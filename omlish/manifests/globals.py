# @omlish-lite
from .loading import ManifestLoader
from ..lite.marshal import unmarshal_obj


##


MANIFEST_LOADER = ManifestLoader(
    instantiator=lambda cls, **kwargs: unmarshal_obj(kwargs, cls),
)
