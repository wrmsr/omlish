# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.lite import marshal as msh


@dc.dataclass(frozen=True)
class OciImageIndex:
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/image-index.md"""

    @dc.dataclass(frozen=True)
    class Manifest:
        digest: str
        size: int

        #

        platform: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(default=None, metadata={msh.OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
        annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={msh.OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

        #

        MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.manifest.v1+json'
        media_type: str = dc.field(default=MEDIA_TYPE, metadata={msh.OBJ_MARSHALER_FIELD_KEY: 'mediaType'})

    manifests: ta.Sequence[Manifest]

    #

    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={msh.OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={msh.OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.index.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={msh.OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


@dc.dataclass(frozen=True)
class OciImageManifest:
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/manifest.md"""

    @dc.dataclass(frozen=True)
    class Config:
        digest: str
        size: int

        #

        MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.config.v1+json'
        media_type: str = dc.field(default=MEDIA_TYPE, metadata={msh.OBJ_MARSHALER_FIELD_KEY: 'mediaType'})

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
        media_type: str = dc.field(default=MEDIA_TYPES['TAR'], metadata={msh.OBJ_MARSHALER_FIELD_KEY: 'mediaType'})

    layers: ta.Sequence[Layer]

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={msh.OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.manifest.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={msh.OBJ_MARSHALER_FIELD_KEY: 'mediaType'})
