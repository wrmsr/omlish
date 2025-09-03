# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.marshal import OBJ_MARSHALER_FIELD_KEY
from omlish.lite.marshal import OBJ_MARSHALER_OMIT_IF_NONE
from omlish.lite.marshal import unmarshal_obj

from .data import OciImageConfig
from .data import OciImageLayer


##


OCI_MEDIA_FIELDS: ta.Collection[str] = frozenset([
    'schema_version',
    'media_type',
])


@dc.dataclass()
class OciMediaDataclass(Abstract):
    SCHEMA_VERSION: ta.ClassVar[int]

    @property
    def schema_version(self) -> int:
        raise TypeError

    MEDIA_TYPE: ta.ClassVar[str]

    @property
    def media_type(self) -> str:
        raise TypeError

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for a in OCI_MEDIA_FIELDS:
            check.in_(a, cls.__dict__)


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


##


@dc.dataclass()
class OciMediaDescriptor:
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


##


@_register_oci_media_dataclass
@dc.dataclass()
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


#


@_register_oci_media_dataclass
@dc.dataclass()
class OciMediaImageManifest(OciMediaDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/manifest.md"""

    config: OciMediaDescriptor  # -> OciMediaImageConfig

    layers: ta.Sequence[OciMediaDescriptor]

    #

    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.manifest.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


#


OCI_IMAGE_LAYER_KIND_MEDIA_TYPES: ta.Mapping[OciImageLayer.Kind, str] = {
    OciImageLayer.Kind.TAR: 'application/vnd.oci.image.layer.v1.tar',
    OciImageLayer.Kind.TAR_GZIP: 'application/vnd.oci.image.layer.v1.tar+gzip',
    OciImageLayer.Kind.TAR_ZSTD: 'application/vnd.oci.image.layer.v1.tar+zstd',
}

OCI_IMAGE_LAYER_KIND_MEDIA_TYPES_: ta.Mapping[str, OciImageLayer.Kind] = {
    v: k
    for k, v in OCI_IMAGE_LAYER_KIND_MEDIA_TYPES.items()
}


#


@_register_oci_media_dataclass
@dc.dataclass()
class OciMediaImageConfig(OciImageConfig, OciMediaDataclass):
    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.config.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


##


OCI_MANIFEST_MEDIA_TYPES: ta.AbstractSet[str] = frozenset([
    OciMediaImageIndex.MEDIA_TYPE,
    OciMediaImageManifest.MEDIA_TYPE,
])
