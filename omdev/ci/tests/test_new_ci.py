# ruff: noqa: PT009 UP006 UP007
import dataclasses as dc
import os.path
import shlex
import shutil
import typing as ta
import unittest

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.lite.json import json_dumps_pretty
from omlish.lite.marshal import marshal_obj

from ...dataserver import BytesDataServerTarget
from ...dataserver import DataServer
from ...dataserver import DataServerTarget
from ...oci.building import BuiltOciImageIndexRepository
from ...oci.building import OciRepositoryBuilder
from ...oci.building import build_oci_index_repository
from ...oci.compression import OciCompression
from ...oci.data import OciImageIndex
from ...oci.data import OciImageLayer
from ...oci.data import OciImageManifest
from ...oci.datarefs import BytesOciDataRef
from ...oci.datarefs import FileOciDataRef
from ...oci.datarefs import open_oci_data_ref
from ...oci.loading import read_oci_repository_root_index
from ...oci.media import OCI_MANIFEST_MEDIA_TYPES
from ...oci.packing import OciLayerPacker
from ...oci.packing import OciLayerUnpacker
from ...oci.repositories import DirectoryOciRepository
from ..ci import Ci
from ..docker.buildcaching import DockerBuildCaching
from .harness import CiHarness


def build_oci_repository_data_server_routes(
        repo_name: str,
        built_repo: BuiltOciImageIndexRepository,
) -> ta.List[DataServer.Route]:
    base_url_path = f'/v2/{repo_name}'

    repo_contents: dict[str, OciRepositoryBuilder.Blob] = {}

    repo_contents[f'{base_url_path}/manifests/latest'] = built_repo.blobs[built_repo.media_index_descriptor.digest]

    for blob in built_repo.blobs.values():
        repo_contents['/'.join([
            base_url_path,
            'manifests' if blob.media_type in OCI_MANIFEST_MEDIA_TYPES else 'blobs',
            blob.digest,
        ])] = blob

    #

    def build_dst(blob: OciRepositoryBuilder.Blob) -> DataServerTarget | None:
        if isinstance(blob.data, BytesOciDataRef):
            return BytesDataServerTarget(
                data=blob.data.data,
                content_type=check.non_empty_str(blob.media_type),
            )

        else:
            with open_oci_data_ref(blob.data) as f:
                data = f.read()

            return BytesDataServerTarget(
                data=data,
                content_type=check.non_empty_str(blob.media_type),
            )

    rts = [
        (p, dst)
        for p, blob in repo_contents.items()
        if (dst := build_dst(blob)) is not None
    ]

    return DataServer.build_routes(*rts)


@dc.dataclass()
class NewDockerBuildCaching(DockerBuildCaching):
    ci_harness: CiHarness

    async def cached_build_docker_image(
            self,
            cache_key: str,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],
    ) -> str:
        image_tag = f'{self.ci_harness.ci_config().service}:{cache_key}'
        image_id = await build_and_tag(image_tag)
        print(image_id)

        #

        temp_dir = os.path.join(self.ci_harness.temp_dir(), 'new_docker')
        os.mkdir(temp_dir)

        print(temp_dir)

        #

        built_image_dir = os.path.join(temp_dir, 'built-image')
        os.mkdir(built_image_dir)

        await asyncio_subprocesses.check_call(
            ' | '.join([
                f'docker save {shlex.quote(image_id)}',
                f'tar x -C {shlex.quote(built_image_dir)}',
            ]),
            shell=True,
        )

        #

        image_index = read_oci_repository_root_index(DirectoryOciRepository(built_image_dir))

        while True:
            child_manifest = check.single(image_index.manifests)
            if isinstance(child_manifest, OciImageManifest):
                image = child_manifest
                break
            image_index = check.isinstance(child_manifest, OciImageIndex)

        #

        image.config.history = None

        #

        input_files = []

        for i, layer in enumerate(image.layers):
            if isinstance(layer.data, FileOciDataRef):
                input_file_path = layer.data.path

            else:
                input_file_path = os.path.join(temp_dir, f'built-layer-{i}.tar')
                with open(input_file_path, 'wb') as input_file:  # noqa
                    with open_oci_data_ref(layer.data) as layer_file:
                        shutil.copyfileobj(layer_file, input_file, length=1024 * 1024)  # noqa

            input_files.append(input_file_path)

        #

        unpacked_file_path = os.path.join(temp_dir, 'unpacked.tar')

        print(unpacked_file_path)

        with OciLayerUnpacker(
                input_files,
                unpacked_file_path,
        ) as lu:
            lu.write()

        #

        num_output_files = 3  # GH actions have this set to 3, the default

        output_file_paths = [
            os.path.join(temp_dir, f'packed-{i}.tar')
            for i in range(num_output_files)
        ]

        print('\n'.join(output_file_paths))

        #

        compression: ta.Optional[OciCompression] = OciCompression.ZSTD

        with OciLayerPacker(
                unpacked_file_path,
                output_file_paths,
                compression=compression,
        ) as lp:
            written = lp.write()

        #

        # FIXME: use prebuilt sha256
        image.layers = [
            OciImageLayer(
                kind=OciImageLayer.Kind.from_compression(compression),
                data=FileOciDataRef(output_file),
            )
            for output_file, output_file_info in written.items()
        ]
        image.config.rootfs.diff_ids = [
            f'sha256:{output_file_info.tar_sha256}'
            for output_file_info in written.values()
        ]

        #

        built_repo = build_oci_index_repository(image_index)

        print(json_dumps_pretty(marshal_obj(built_repo.media_index)))

        #

        data_server_routes = build_oci_repository_data_server_routes(
            cache_key,
            built_repo,
        )

        print(data_server_routes)

        #

        raise NotImplementedError


class TestNewCi(unittest.IsolatedAsyncioTestCase):
    async def test_new_ci(self):
        if not shutil.which('docker'):
            self.skipTest('no docker')

        async with CiHarness() as ci_harness:
            async with Ci(
                config=ci_harness.ci_config(),

                docker_build_caching=NewDockerBuildCaching(ci_harness),
                docker_image_pulling=ci_harness.docker_image_pulling_impl(),
            ) as ci:
                image_id = await ci.resolve_ci_image()
                print(image_id)
