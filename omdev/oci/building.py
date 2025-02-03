# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import json
import typing as ta

from omlish.lite.check import check
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj

from .data import OciDataclass
from .data import OciImageConfig
from .data import OciImageIndex
from .data import OciImageLayer
from .data import OciImageManifest
from .datarefs import BytesOciDataRef
from .datarefs import OciDataRef
from .datarefs import OciDataRefInfo
from .datarefs import open_oci_data_ref
from .media import OCI_IMAGE_LAYER_KIND_MEDIA_TYPES
from .media import OciMediaDataclass
from .media import OciMediaDescriptor
from .media import OciMediaImageConfig
from .media import OciMediaImageIndex
from .media import OciMediaImageManifest
from .media import unmarshal_oci_media_dataclass


OciMediaDataclassT = ta.TypeVar('OciMediaDataclassT', bound='OciMediaDataclass')


##


class OciRepositoryBuilder:
    @dc.dataclass(frozen=True)
    class Blob:
        digest: str

        data: OciDataRef
        info: OciDataRefInfo

        media_type: ta.Optional[str] = None

        #

        def read(self) -> bytes:
            with open_oci_data_ref(self.data) as f:
                return f.read()

        def read_json(self) -> ta.Any:
            return json.loads(self.read().decode('utf-8'))

        def read_media(
                self,
                cls: ta.Type[OciMediaDataclassT] = OciMediaDataclass,  # type: ignore[assignment]
        ) -> OciMediaDataclassT:
            mt = check.non_empty_str(self.media_type)
            dct = self.read_json()
            obj = unmarshal_oci_media_dataclass(
                dct,
                media_type=mt,
            )
            return check.isinstance(obj, cls)

    def __init__(self) -> None:
        super().__init__()

        self._blobs: ta.Dict[str, OciRepositoryBuilder.Blob] = {}

    #

    def get_blobs(self) -> ta.Dict[str, Blob]:
        return dict(self._blobs)

    def add_blob(
            self,
            r: OciDataRef,
            ri: ta.Optional[OciDataRefInfo] = None,
            *,
            media_type: ta.Optional[str] = None,
    ) -> Blob:
        if ri is None:
            ri = OciDataRefInfo(r)

        if (dg := ri.digest()) in self._blobs:
            raise KeyError(ri.digest())

        blob = self.Blob(
            digest=dg,

            data=r,
            info=ri,

            media_type=media_type,
        )

        self._blobs[dg] = blob

        return blob

    #

    def marshal_media(self, obj: OciMediaDataclass) -> bytes:
        check.isinstance(obj, OciMediaDataclass)
        m = marshal_obj(obj)
        j = json_dumps_compact(m)
        b = j.encode('utf-8')
        return b

    def add_media(self, obj: OciMediaDataclass) -> OciMediaDescriptor:
        b = self.marshal_media(obj)

        r = BytesOciDataRef(b)
        ri = OciDataRefInfo(r)
        self.add_blob(
            r,
            ri,
            media_type=obj.media_type,
        )

        return OciMediaDescriptor(
            media_type=obj.media_type,
            digest=ri.digest(),
            size=ri.size(),
        )

    #

    def to_media(self, obj: OciDataclass) -> ta.Union[OciMediaDataclass, OciMediaDescriptor]:
        def make_kw(*exclude):
            return {
                a: v
                for f in dc.fields(obj)
                if (a := f.name) not in exclude
                for v in [getattr(obj, a)]
                if v is not None
            }

        if isinstance(obj, OciImageIndex):
            return OciMediaImageIndex(
                **make_kw('manifests'),
                manifests=[
                    self.add_data(m)
                    for m in obj.manifests
                ],
            )

        elif isinstance(obj, OciImageManifest):
            return OciMediaImageManifest(
                **make_kw('config', 'layers'),
                config=self.add_data(obj.config),
                layers=[
                    self.add_data(l)
                    for l in obj.layers
                ],
            )

        elif isinstance(obj, OciImageLayer):
            ri = OciDataRefInfo(obj.data)
            mt = OCI_IMAGE_LAYER_KIND_MEDIA_TYPES[obj.kind]
            self.add_blob(
                obj.data,
                ri,
                media_type=mt,
            )
            return OciMediaDescriptor(
                media_type=mt,
                digest=ri.digest(),
                size=ri.size(),
            )

        elif isinstance(obj, OciImageConfig):
            return OciMediaImageConfig(**make_kw())

        else:
            raise TypeError(obj)

    def add_data(self, obj: OciDataclass) -> OciMediaDescriptor:
        ret = self.to_media(obj)

        if isinstance(ret, OciMediaDataclass):
            return self.add_media(ret)

        elif isinstance(ret, OciMediaDescriptor):
            return ret

        else:
            raise TypeError(ret)


##


@dc.dataclass(frozen=True)
class BuiltOciImageIndexRepository:
    index: OciImageIndex

    media_index_descriptor: OciMediaDescriptor
    media_index: OciMediaImageIndex

    blobs: ta.Mapping[str, OciRepositoryBuilder.Blob]


def build_oci_index_repository(index: OciImageIndex) -> BuiltOciImageIndexRepository:
    builder = OciRepositoryBuilder()

    media_index_descriptor = builder.add_data(index)

    blobs = builder.get_blobs()

    media_index = blobs[media_index_descriptor.digest].read_media(OciMediaImageIndex)

    return BuiltOciImageIndexRepository(
        index=index,

        media_index_descriptor=media_index_descriptor,
        media_index=media_index,

        blobs=blobs,
    )
