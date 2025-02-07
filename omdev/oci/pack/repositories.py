# ruff: noqa: UP006 UP007
# @omlish-lite
import copy
import os.path
import shutil
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import ExitStacked
from omlish.lite.timing import log_timing_context
from omlish.os.temp import temp_dir_context

from ...oci.building import BuiltOciImageIndexRepository
from ...oci.building import build_oci_index_repository
from ...oci.compression import OciCompression
from ...oci.data import OciImageIndex
from ...oci.data import OciImageLayer
from ...oci.data import OciImageManifest
from ...oci.datarefs import FileOciDataRef
from ...oci.datarefs import open_oci_data_ref
from ...oci.loading import read_oci_repository_root_index
from ...oci.tars import WrittenOciDataTarFileInfo
from ..repositories import OciRepository
from .packing import OciLayerPacker
from .unpacking import OciLayerUnpacker


##


class OciPackedRepositoryBuilder(ExitStacked):
    def __init__(
            self,
            source_repo: OciRepository,
            *,
            temp_dir: ta.Optional[str] = None,

            num_packed_files: int = 3,  # GH actions have this set to 3, the default
            packed_compression: ta.Optional[OciCompression] = OciCompression.ZSTD,
    ) -> None:
        super().__init__()

        self._source_repo = source_repo

        self._given_temp_dir = temp_dir

        check.arg(num_packed_files > 0)
        self._num_packed_files = num_packed_files

        self._packed_compression = packed_compression

    @cached_nullary
    def _temp_dir(self) -> str:
        if (given := self._given_temp_dir) is not None:
            return given
        else:
            return self._enter_context(temp_dir_context())  # noqa

    #

    @cached_nullary
    def _source_image_index(self) -> OciImageIndex:
        image_index = read_oci_repository_root_index(self._source_repo)

        while True:
            child_manifest = check.single(image_index.manifests)
            if isinstance(child_manifest, OciImageManifest):
                break
            image_index = check.isinstance(child_manifest, OciImageIndex)

        return image_index

    @staticmethod
    def _get_index_image(image_index: OciImageIndex) -> OciImageManifest:
        child_index = check.single(image_index.manifests)
        return check.isinstance(child_index, OciImageManifest)

    @cached_nullary
    def _source_image_manifest(self) -> OciImageManifest:
        return self._get_index_image(self._source_image_index())

    #

    @cached_nullary
    def _extracted_layer_tar_files(self) -> ta.List[str]:
        image = self._source_image_manifest()

        layer_tar_files = []

        for i, layer in enumerate(image.layers):
            if isinstance(layer.data, FileOciDataRef):
                input_file_path = layer.data.path

            else:
                input_file_path = os.path.join(self._temp_dir(), f'save-layer-{i}.tar')
                with open(input_file_path, 'wb') as input_file:  # noqa
                    with open_oci_data_ref(layer.data) as layer_file:
                        shutil.copyfileobj(layer_file, input_file, length=1024 * 1024)  # noqa

            layer_tar_files.append(input_file_path)

        return layer_tar_files

    #

    @cached_nullary
    def _unpacked_tar_file(self) -> str:
        layer_tar_files = self._extracted_layer_tar_files()
        unpacked_file = os.path.join(self._temp_dir(), 'unpacked.tar')

        with log_timing_context(f'Unpacking docker image {self._source_repo}'):
            with OciLayerUnpacker(
                    layer_tar_files,
                    unpacked_file,
            ) as lu:
                lu.write()

        return unpacked_file

    #

    @cached_nullary
    def _packed_tar_files(self) -> ta.Mapping[str, WrittenOciDataTarFileInfo]:
        unpacked_tar_file = self._unpacked_tar_file()

        packed_tar_files = [
            os.path.join(self._temp_dir(), f'packed-{i}.tar')
            for i in range(self._num_packed_files)
        ]

        with log_timing_context(f'Packing docker image {self._source_repo}'):
            with OciLayerPacker(
                    unpacked_tar_file,
                    packed_tar_files,
                    compression=self._packed_compression,
            ) as lp:
                return lp.write()

    #

    @cached_nullary
    def _packed_image_index(self) -> OciImageIndex:
        image_index = copy.deepcopy(self._source_image_index())

        image = self._get_index_image(image_index)

        image.config.history = None

        written = self._packed_tar_files()

        # FIXME: use prebuilt sha256
        image.layers = [
            OciImageLayer(
                kind=OciImageLayer.Kind.from_compression(self._packed_compression),
                data=FileOciDataRef(output_file),
            )
            for output_file, output_file_info in written.items()
        ]

        image.config.rootfs.diff_ids = [
            f'sha256:{output_file_info.tar_sha256}'
            for output_file_info in written.values()
        ]

        return image_index

    #

    @cached_nullary
    def build(self) -> BuiltOciImageIndexRepository:
        return build_oci_index_repository(self._packed_image_index())
