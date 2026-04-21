import typing as ta

from omlish import dataclasses as dc
from omlish import marshal as msh

from ..services.responses import ResponseMetadata


if ta.TYPE_CHECKING:
    from .retry import AnyRetryService


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='RetryServiceResponseMetadata',
#     type='ResponseMetadata',
# )
@dc.dataclass(frozen=True)
@msh.update_fields_options(['retry_service'], no_marshal=True, no_unmarshal=True)
class RetryServiceResponseMetadata(ResponseMetadata):
    num_retries: int

    _: dc.KW_ONLY

    retry_service: AnyRetryService | None = None
