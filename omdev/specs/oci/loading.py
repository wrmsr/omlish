# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import json
import typing as ta

from omlish.lite.check import check

from .data import OciImageConfig
from .data import OciImageIndex
from .data import OciImageLayer
from .data import OciImageManifest
from .data import is_empty_oci_dataclass
from .media import OCI_IMAGE_LAYER_KIND_MEDIA_TYPES_
from .media import OCI_MEDIA_FIELDS
from .media import OciMediaDescriptor
from .media import OciMediaImageConfig
from .media import OciMediaImageIndex
from .media import OciMediaImageManifest
from .media import unmarshal_oci_media_dataclass
from .repositories import FileOciRepository
from .repositories import OciRepository


T = ta.TypeVar('T')


##


class OciRepositoryLoader:
    def __init__(
            self,
            repo: OciRepository,
    ) -> None:
        super().__init__()

        self._repo = repo

    #

    def load_object(
            self,
            data: bytes,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
            *,
            media_type: ta.Optional[str] = None,
    ) -> T:
        text = data.decode('utf-8')
        dct = json.loads(text)
        obj = unmarshal_oci_media_dataclass(
            dct,
            media_type=media_type,
        )
        return check.isinstance(obj, cls)

    def read_object(
            self,
            digest: str,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
            *,
            media_type: ta.Optional[str] = None,
    ) -> T:
        data = self._repo.read_blob(digest)
        return self.load_object(
            data,
            cls,
            media_type=media_type,
        )

    def read_descriptor(
            self,
            desc: OciMediaDescriptor,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
    ) -> ta.Any:
        return self.read_object(
            desc.digest,
            cls,
            media_type=desc.media_type,
        )

    #

    def from_media(self, obj: ta.Any) -> ta.Any:
        def make_kw(*exclude):
            return {
                a: getattr(obj, a)
                for f in dc.fields(obj)
                if (a := f.name) not in OCI_MEDIA_FIELDS
                and a not in exclude
            }

        if isinstance(obj, OciMediaImageConfig):
            return OciImageConfig(**make_kw())

        elif isinstance(obj, OciMediaImageManifest):
            return OciImageManifest(
                **make_kw('config', 'layers'),
                config=self.from_media(self.read_descriptor(obj.config)),
                layers=[
                    OciImageLayer(
                        kind=lk,
                        data=self._repo.ref_blob(l.digest),
                    )
                    for l in obj.layers
                    if (lk := OCI_IMAGE_LAYER_KIND_MEDIA_TYPES_.get(l.media_type)) is not None
                ],
            )

        elif isinstance(obj, OciMediaImageIndex):
            return OciImageIndex(
                **make_kw('manifests'),
                manifests=[
                    fm
                    for m in obj.manifests
                    if self._repo.contains_blob(m.digest)
                    for fm in [self.from_media(self.read_descriptor(m))]
                    if not is_empty_oci_dataclass(fm)
                ],
            )

        else:
            raise TypeError(obj)


##


def read_oci_repository_root_index(
        obj: ta.Any,
        *,
        file_name: str = 'index.json',
) -> OciImageIndex:
    file_repo = check.isinstance(OciRepository.of(obj), FileOciRepository)

    repo_ldr = OciRepositoryLoader(file_repo)

    media_image_idx = repo_ldr.load_object(file_repo.read_file(file_name), OciMediaImageIndex)

    image_idx = repo_ldr.from_media(media_image_idx)

    return check.isinstance(image_idx, OciImageIndex)
