# ruff: noqa: PT009 UP006 UP007
import abc
import asyncio
import dataclasses as dc
import os.path
import shlex
import shutil
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.lite.json import json_dumps_pretty
from omlish.lite.marshal import marshal_obj
from omlish.logs.standard import configure_standard_logging

from ...dataserver.http import DataServerHttpHandler
from ...dataserver.routes import DataServerRoute
from ...dataserver.server import DataServer
from ...dataserver.targets import BytesDataServerTarget
from ...dataserver.targets import DataServerTarget
from ...dataserver.targets import FileDataServerTarget
from ...oci.building import build_oci_index_repository
from ...oci.compression import OciCompression
from ...oci.data import OciImageIndex
from ...oci.data import OciImageLayer
from ...oci.data import OciImageManifest
from ...oci.datarefs import FileOciDataRef
from ...oci.datarefs import open_oci_data_ref
from ...oci.dataserver import build_oci_repository_data_server_routes
from ...oci.loading import read_oci_repository_root_index
from ...oci.packing import OciLayerPacker
from ...oci.packing import OciLayerUnpacker
from ...oci.repositories import DirectoryOciRepository
from .harness import CiHarness
from .serving import serve_for_docker


@dc.dataclass(frozen=True)
class NewCiManifest:
    @dc.dataclass(frozen=True)
    class Route:
        paths: ta.Sequence[str]

        content_type: str
        content_length: int

        @dc.dataclass(frozen=True)
        class Target(abc.ABC):  # noqa
            pass

        @dc.dataclass(frozen=True)
        class BytesTarget(Target):
            data: bytes

        @dc.dataclass(frozen=True)
        class CacheKeyTarget(Target):
            key: str

        target: Target

        def __post_init__(self) -> None:
            check.not_isinstance(self.paths, str)

    routes: ta.Sequence[Route]


def build_new_ci_manifest(data_server_routes: ta.Iterable[DataServerRoute]) -> NewCiManifest:
    routes: ta.List[NewCiManifest.Route] = []

    for data_server_route in data_server_routes:
        content_length: int

        data_server_target = data_server_route.target
        target: NewCiManifest.Route.Target
        if isinstance(data_server_target, BytesDataServerTarget):
            bytes_data = check.isinstance(data_server_target.data, bytes)
            content_length = len(bytes_data)
            target = NewCiManifest.Route.BytesTarget(bytes_data)

        elif isinstance(data_server_target, FileDataServerTarget):
            file_path = check.non_empty_str(data_server_target.file_path)
            content_length = os.path.getsize(file_path)
            # FIXME:
            target = NewCiManifest.Route.CacheKeyTarget(file_path)

        else:
            raise TypeError(data_server_target)

        routes.append(NewCiManifest.Route(
            paths=data_server_route.paths,

            content_type=check.non_empty_str(data_server_target.content_type),
            content_length=content_length,

            target=target,
        ))

    return NewCiManifest(
        routes=routes,
    )


def build_new_ci_data_server_routes(manifest: NewCiManifest) -> ta.List[DataServerRoute]:
    routes: ta.List[DataServerRoute] = []

    for manifest_route in manifest.routes:
        manifest_target = manifest_route.target
        target: DataServerTarget

        if isinstance(manifest_target, NewCiManifest.Route.BytesTarget):
            target = DataServerTarget.of(manifest_target.data)

        elif isinstance(manifest_target, NewCiManifest.Route.CacheKeyTarget):
            # FIXME:
            target = DataServerTarget.of(file_path=manifest_target.key)

        else:
            raise TypeError(manifest_target)

        routes.append(DataServerRoute(
            paths=manifest_route.paths,
            target=target,
        ))

    return routes


async def run_new_ci(
        *,
        image_id: str,
        cache_key: str,
        temp_dir: str,
) -> None:
    new_temp_dir = os.path.join(temp_dir, 'new')
    os.mkdir(new_temp_dir)

    print(new_temp_dir)

    #

    built_image_dir = os.path.join(new_temp_dir, 'built-image')
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
            input_file_path = os.path.join(new_temp_dir, f'built-layer-{i}.tar')
            with open(input_file_path, 'wb') as input_file:  # noqa
                with open_oci_data_ref(layer.data) as layer_file:
                    shutil.copyfileobj(layer_file, input_file, length=1024 * 1024)  # noqa

        input_files.append(input_file_path)

    #

    unpacked_file_path = os.path.join(new_temp_dir, 'unpacked.tar')

    print(unpacked_file_path)

    with OciLayerUnpacker(
            input_files,
            unpacked_file_path,
    ) as lu:
        lu.write()

    #

    num_output_files = 3  # GH actions have this set to 3, the default

    output_file_paths = [
        os.path.join(new_temp_dir, f'packed-{i}.tar')
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

    print(json_dumps_pretty(marshal_obj(data_server_routes, ta.List[DataServerRoute])))

    #

    new_ci_manifest = build_new_ci_manifest(data_server_routes)

    print(json_dumps_pretty(marshal_obj(new_ci_manifest)))

    #

    new_data_server_routes = build_new_ci_data_server_routes(new_ci_manifest)

    data_server = DataServer(DataServer.HandlerRoute.of_(*new_data_server_routes))

    #

    port = 5021

    image_url = f'localhost:{port}/{cache_key}'

    print(f'docker run --rm --pull always {image_url} uname -a')

    serve_for_docker(
        port,
        DataServerHttpHandler(data_server),
    )


# @dc.dataclass()
# class NewDockerBuildCaching(DockerBuildCaching):
#     ci_harness: CiHarness
#
#     async def cached_build_docker_image(
#             self,
#             cache_key: str,
#             build_and_tag: ta.Callable[[str], ta.Awaitable[str]],
#     ) -> str:
#         image_tag = f'{self.ci_harness.ci_config().service}:{cache_key}'
#         image_id = await build_and_tag(image_tag)
#         print(image_id)
#         raise NotImplementedError


async def a_main() -> None:
    configure_standard_logging()

    async with CiHarness() as ci_harness:
        # async with Ci(
        #         config=ci_harness.ci_config(),
        #
        #         docker_build_caching=NewDockerBuildCaching(ci_harness),
        #         docker_image_pulling=ci_harness.docker_image_pulling_impl(),
        # ) as ci:
        #     image_id = await ci.resolve_ci_image()
        #
        #     print(image_id)

        async with ci_harness.make_ci() as ci:
            image_id = await ci.resolve_ci_image()

            await run_new_ci(
                image_id=image_id,
                cache_key=ci.ci_image_cache_key(),
                temp_dir=ci_harness.temp_dir(),
            )


if __name__ == '__main__':
    asyncio.run(a_main())
