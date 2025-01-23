# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.lite.marshal import OBJ_MARSHALER_FIELD_KEY
from omlish.lite.marshal import OBJ_MARSHALER_OMIT_IF_NONE
from omlish.lite.marshal import unmarshal_obj


##


_REGISTERED_OCI_MEDIA_TYPES: ta.Dict[str, type] = {}


def _register_oci_dataclass_media_type(cls):
    check.isinstance(cls, type)
    check.arg(dc.is_dataclass(cls))
    mt = check.non_empty_str(cls.MEDIA_TYPE)
    check.not_in(mt, _REGISTERED_OCI_MEDIA_TYPES)
    _REGISTERED_OCI_MEDIA_TYPES[mt] = cls
    return cls


def get_registered_oci_media_type(media_type: str) -> ta.Optional[str]:
    return _REGISTERED_OCI_MEDIA_TYPES.get(media_type)


def unmarshal_oci_dataclass(dct: ta.Mapping[str, ta.Any]) -> ta.Any:
    mt = check.non_empty_str(dct['mediaType'])
    cls = _REGISTERED_OCI_MEDIA_TYPES[mt]
    return unmarshal_obj(dct, cls)


##


@_register_oci_dataclass_media_type
@dc.dataclass(frozen=True)
class OciImageIndex:
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/image-index.md"""

    @dc.dataclass(frozen=True)
    class Manifest:
        digest: str
        size: int

        #

        platform: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
        annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

        #

        MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.manifest.v1+json'
        media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})

    manifests: ta.Sequence[Manifest]

    #

    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.index.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


@_register_oci_dataclass_media_type
@dc.dataclass(frozen=True)
class OciImageManifest:
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/manifest.md"""

    @dc.dataclass(frozen=True)
    class Config:
        digest: str
        size: int

        #

        MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.config.v1+json'
        media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})

    config: Config

    @dc.dataclass(frozen=True)
    class Layer:
        digest: str
        size: int

        #

        MEDIA_TYPES: ta.ClassVar[ta.Mapping[str, str]] = {
            'TAR': 'application/vnd.oci.image.layer.v1.tar',
            'TAR_GZIP': 'application/vnd.oci.image.layer.v1.tar+gzip',
            'TAR_ZSTD': 'application/vnd.oci.image.layer.v1.tar+zstd',
        }
        media_type: str = dc.field(default=MEDIA_TYPES['TAR'], metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})

    layers: ta.Sequence[Layer]

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.manifest.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})
