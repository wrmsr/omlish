# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.lite.marshal import OBJ_MARSHALER_FIELD_KEY
from omlish.lite.marshal import OBJ_MARSHALER_OMIT_IF_NONE
from omlish.lite.marshal import unmarshal_obj


##


@dc.dataclass(frozen=True)
class OciDataclass(abc.ABC):  # noqa
    pass


##


@dc.dataclass(frozen=True)
class OciImageConfig(OciDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/config.md"""

    architecture: str
    os: str

    @dc.dataclass(frozen=True)
    class RootFs:
        type: str
        diff_ids: ta.Sequence[str]

    rootfs: RootFs

    #

    created: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    author: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    os_version: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'os.version', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    os_features: ta.Optional[ta.Sequence[str]] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'os.features', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    variant: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    """
    config object, OPTIONAL
        User string, OPTIONAL
        ExposedPorts object, OPTIONAL
        Env array of strings, OPTIONAL
        Entrypoint array of strings, OPTIONAL
        Cmd array of strings, OPTIONAL
        Volumes object, OPTIONAL
        WorkingDir string, OPTIONAL
        Labels object, OPTIONAL
        StopSignal string, OPTIONAL
        ArgsEscaped boolean, OPTIONAL
        Memory integer, OPTIONAL
        MemorySwap integer, OPTIONAL
        CpuShares integer, OPTIONAL
        Healthcheck object, OPTIONAL
    """
    config: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    @dc.dataclass(frozen=True)
    class History:
        created: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        author: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        created_by: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        comment: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        empty_layer: ta.Optional[bool] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    history: ta.Optional[ta.Sequence[History]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})


##


@dc.dataclass(frozen=True)
class OciMediaDataclass(OciDataclass, abc.ABC):  # noqa
    SCHEMA_VERSION: ta.ClassVar[int]
    MEDIA_TYPE: ta.ClassVar[str]


_REGISTERED_OCI_MEDIA_DATACLASSES: ta.Dict[str, ta.Type[OciMediaDataclass]] = {}


def _register_oci_media_dataclass(cls):
    check.issubclass(cls, OciMediaDataclass)
    check.arg(dc.is_dataclass(cls))
    mt = check.non_empty_str(cls.__dict__['MEDIA_TYPE'])
    check.not_in(mt, _REGISTERED_OCI_MEDIA_DATACLASSES)
    _REGISTERED_OCI_MEDIA_DATACLASSES[mt] = cls
    return cls


def get_registered_oci_media_dataclass(media_type: str) -> ta.Optional[ta.Type[OciMediaDataclass]]:
    return _REGISTERED_OCI_MEDIA_DATACLASSES.get(media_type)


def unmarshal_oci_media_dataclass(
        dct: ta.Mapping[str, ta.Any],
        *,
        media_type: ta.Optional[str] = None,
) -> ta.Any:
    if media_type is None:
        media_type = check.non_empty_str(dct['mediaType'])
    cls = _REGISTERED_OCI_MEDIA_DATACLASSES[media_type]
    return unmarshal_obj(dct, cls)


#


@dc.dataclass(frozen=True)
class OciMediaDescriptor(OciDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/descriptor.md#properties"""  # noqa

    media_type: str = dc.field(metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})
    digest: str
    size: int

    #

    urls: ta.Optional[ta.Sequence[str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    data: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    artifact_type: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'artifactType', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    platform: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa


@_register_oci_media_dataclass
@dc.dataclass(frozen=True)
class OciMediaImageIndex(OciMediaDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/image-index.md"""

    manifests: ta.Sequence[OciMediaDescriptor]  # -> OciMediaImageIndex | OciMediaImageManifest

    #

    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.index.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


@_register_oci_media_dataclass
@dc.dataclass(frozen=True)
class OciMediaImageManifest(OciMediaDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/manifest.md"""

    config: OciMediaDescriptor  # -> OciMediaImageConfig

    # MEDIA_TYPES: ta.ClassVar[ta.Mapping[str, str]] = {
    #     'TAR': 'application/vnd.oci.image.layer.v1.tar',
    #     'TAR_GZIP': 'application/vnd.oci.image.layer.v1.tar+gzip',
    #     'TAR_ZSTD': 'application/vnd.oci.image.layer.v1.tar+zstd',
    # }
    layers: ta.Sequence[OciMediaDescriptor]

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.manifest.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


@_register_oci_media_dataclass
@dc.dataclass(frozen=True)
class OciMediaImageConfig(OciImageConfig, OciMediaDataclass):
    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.config.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})
