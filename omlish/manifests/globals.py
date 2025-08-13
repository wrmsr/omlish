# @omlish-lite
from ..lite.marshal import unmarshal_obj
from .loading import ManifestLoader


##


MANIFEST_LOADER = ManifestLoader(
    cls_instantiator=lambda cls, **kwargs: unmarshal_obj(kwargs, cls),
)
