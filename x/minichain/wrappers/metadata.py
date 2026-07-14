import typing as ta

from omcore import dataclasses as dc
from omcore import marshal as msh

from ..services.responses import ResponseMetadata


if ta.TYPE_CHECKING:
    from .retry import AnyRetryService


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='RetryServiceResponseMetadata',
#     type='ResponseMetadata',
# )
@dc.dataclass(frozen=True)
@msh.update_field_options('retry_service', no_marshal=True, no_unmarshal=True)
class RetryServiceResponseMetadata(ResponseMetadata):
    num_retries: int

    _: dc.KW_ONLY

    retry_service: AnyRetryService | None = None
