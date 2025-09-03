# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import enum
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.marshal import OBJ_MARSHALER_FIELD_KEY
from omlish.lite.marshal import OBJ_MARSHALER_OMIT_IF_NONE

from .compression import OciCompression
from .datarefs import OciDataRef


##


@dc.dataclass()
class OciDataclass(Abstract):
    pass


##


@dc.dataclass()
class OciImageIndex(OciDataclass):
    manifests: ta.List[ta.Union['OciImageIndex', 'OciImageManifest']]

    annotations: ta.Optional[ta.Dict[str, str]] = None


#


@dc.dataclass()
class OciImageManifest(OciDataclass):
    config: 'OciImageConfig'

    layers: ta.List['OciImageLayer']

    annotations: ta.Optional[ta.Dict[str, str]] = None


#


@dc.dataclass()
class OciImageLayer(OciDataclass):
    class Kind(enum.Enum):
        TAR = enum.auto()
        TAR_GZIP = enum.auto()
        TAR_ZSTD = enum.auto()

        @property
        def compression(self) -> ta.Optional[OciCompression]:
            if self is self.TAR:
                return None
            elif self is self.TAR_GZIP:
                return OciCompression.GZIP
            elif self is self.TAR_ZSTD:
                return OciCompression.ZSTD
            else:
                raise ValueError(self)

        @classmethod
        def from_compression(cls, compression: ta.Optional[OciCompression]) -> 'OciImageLayer.Kind':
            if compression is None:
                return cls.TAR
            elif compression == OciCompression.GZIP:
                return cls.TAR_GZIP
            elif compression == OciCompression.ZSTD:
                return cls.TAR_ZSTD
            else:
                raise ValueError(compression)

    kind: Kind

    data: OciDataRef


#


@dc.dataclass()
class OciImageConfig(OciDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/config.md"""

    architecture: str
    os: str

    @dc.dataclass()
    class RootFs:
        type: str
        diff_ids: ta.List[str]

    rootfs: RootFs

    #

    created: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    author: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    os_version: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'os.version', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    os_features: ta.Optional[ta.List[str]] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'os.features', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
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
    config: ta.Optional[ta.Dict[str, ta.Any]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    @dc.dataclass()
    class History:
        created: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        author: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        created_by: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        comment: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        empty_layer: ta.Optional[bool] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    history: ta.Optional[ta.List[History]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})


##


def is_empty_oci_dataclass(obj: OciDataclass) -> bool:
    if not isinstance(obj, OciDataclass):
        raise TypeError(obj)

    elif isinstance(obj, OciImageIndex):
        return not obj.manifests

    elif isinstance(obj, OciImageManifest):
        return not obj.layers

    else:
        return False


##


def get_single_leaf_oci_image_index(image_index: OciImageIndex) -> OciImageIndex:
    while True:
        child_manifest = check.single(image_index.manifests)
        if isinstance(child_manifest, OciImageManifest):
            break
        image_index = check.isinstance(child_manifest, OciImageIndex)

    return image_index


def get_single_oci_image_manifest(image_index: OciImageIndex) -> OciImageManifest:
    child_index = check.single(image_index.manifests)
    return check.isinstance(child_index, OciImageManifest)
