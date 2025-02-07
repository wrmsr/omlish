# ruff: noqa: PT009 UP006 UP007
import asyncio
import dataclasses as dc
import typing as ta

from omlish.lite.json import json_dumps_pretty
from omlish.lite.marshal import marshal_obj
from omlish.logs.standard import configure_standard_logging

from ...dataserver.server import DataServer
from ...dataserver.targets import DataServerTarget
from ...oci.dataserver import build_oci_repository_data_server_routes
from ..ci import Ci
from ..docker.buildcaching import DockerBuildCaching
from ..docker.cacheserved import build_cache_served_docker_image_data_server_routes
from ..docker.cacheserved import build_cache_served_docker_image_manifest
from ..docker.dataserver import DockerDataServer
from ..docker.packing import PackedDockerImageIndexRepositoryBuilder
from .harness import CiHarness


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

            new_ci_manifest = build_cache_served_docker_image_manifest(
                data_server_routes,
                lambda file_path: file_path,  # FIXME: upload lol
            )

            print(json_dumps_pretty(marshal_obj(new_ci_manifest)))

            ####

            port = 5021

            image_url = f'localhost:{port}/{cache_key}'

            print(f'docker run --rm --pull always {image_url} uname -a')

            new_data_server_routes = build_cache_served_docker_image_data_server_routes(
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
