# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import dataclasses as dc
import enum
import typing as ta

from omlish.lite.marshal import OBJ_MARSHALER_FIELD_KEY
from omlish.lite.marshal import OBJ_MARSHALER_OMIT_IF_NONE

from .datarefs import OciDataRef


##


@dc.dataclass()
class OciDataclass(abc.ABC):  # noqa
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
