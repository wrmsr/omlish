# ruff: noqa: PT009 UP006 UP007
import abc
import asyncio
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.lite.json import json_dumps_pretty
from omlish.lite.marshal import marshal_obj
from omlish.logs.standard import configure_standard_logging

from ...dataserver.routes import DataServerRoute
from ...dataserver.server import DataServer
from ...dataserver.targets import BytesDataServerTarget
from ...dataserver.targets import DataServerTarget
from ...dataserver.targets import FileDataServerTarget
from ...oci.dataserver import build_oci_repository_data_server_routes
from ..ci import Ci
from ..docker.buildcaching import DockerBuildCaching
from ..docker.dataserver import DockerDataServer
from ..docker.packing import PackedDockerImageIndexRepositoryBuilder
from .harness import CiHarness


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


def build_new_ci_manifest(
        data_server_routes: ta.Iterable[DataServerRoute],
        make_file_cache_key: ta.Callable[[str], str],
) -> NewCiManifest:
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
            cache_key = make_file_cache_key(file_path)
            target = NewCiManifest.Route.CacheKeyTarget(cache_key)

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


def build_new_ci_data_server_routes(
        manifest: NewCiManifest,
        make_cache_key_target: ta.Callable[..., DataServerTarget],
) -> ta.List[DataServerRoute]:
    routes: ta.List[DataServerRoute] = []

    for manifest_route in manifest.routes:
        manifest_target = manifest_route.target

        target_kwargs: dict = dict(
            content_type=manifest_route.content_type,
            content_length=manifest_route.content_length,
        )

        target: DataServerTarget

        if isinstance(manifest_target, NewCiManifest.Route.BytesTarget):
            target = DataServerTarget.of(manifest_target.data, **target_kwargs)

        elif isinstance(manifest_target, NewCiManifest.Route.CacheKeyTarget):
            target = make_cache_key_target(manifest_target.key, **target_kwargs)

        else:
            raise TypeError(manifest_target)

        routes.append(DataServerRoute(
            paths=manifest_route.paths,
            target=target,
        ))

    return routes


# async def run_new_ci(
#         *,
#         image_id: str,
#         cache_key: str,
# ) -> None:
#     new_data_server_routes = build_new_ci_data_server_routes(new_ci_manifest)
#
#     data_server = DataServer(DataServer.HandlerRoute.of_(*new_data_server_routes))
#
#     #
#
#     port = 5021
#
#     image_url = f'localhost:{port}/{cache_key}'
#
#     print(f'docker run --rm --pull always {image_url} uname -a')
#
#     # serve_for_docker(
#     #     port,
#     #     DataServerHttpHandler(data_server),
#     # )
#     data_server  # noqa


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

        with PackedDockerImageIndexRepositoryBuilder(
                image_id=image_id,
        ) as drb:
            built_repo = drb.packed_image_index_repository()

            data_server_routes = build_oci_repository_data_server_routes(
                cache_key,
                built_repo,
            )

            new_ci_manifest = build_new_ci_manifest(
                data_server_routes,
                lambda file_path: file_path,  # FIXME: upload lol
            )

            print(json_dumps_pretty(marshal_obj(new_ci_manifest)))

            ####

            port = 5021

            image_url = f'localhost:{port}/{cache_key}'

            print(f'docker run --rm --pull always {image_url} uname -a')

            new_data_server_routes = build_new_ci_data_server_routes(
                new_ci_manifest,
                lambda new_ci_target_cache_key, **target_kwargs: DataServerTarget.of(
                    file_path=new_ci_target_cache_key,
                    **target_kwargs,
                ),
            )

            data_server = DataServer(DataServer.HandlerRoute.of_(*new_data_server_routes))

            async with DockerDataServer(
                    port,
                    data_server,
            ) as dds:
                dds_run_task = asyncio.create_task(dds.run())
                try:
                    await asyncio.sleep(600.)

                finally:
                    dds.stop_event.set()
                    await dds_run_task

        return image_tag


async def a_main() -> None:
    configure_standard_logging('DEBUG')

    async with CiHarness() as ci_harness:
        for _ in range(2):
            async with Ci(
                    config=ci_harness.ci_config(),

                    docker_build_caching=NewDockerBuildCaching(ci_harness),
                    docker_image_pulling=ci_harness.docker_image_pulling_impl(),
            ) as ci:
                image_id = await ci.resolve_ci_image()

                print(image_id)


if __name__ == '__main__':
    asyncio.run(a_main())
