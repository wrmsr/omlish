# ruff: noqa: PT009 UP006 UP007
import asyncio
import dataclasses as dc
import os.path
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.lite.json import json_dumps_pretty
from omlish.lite.logs import log
from omlish.lite.marshal import marshal_obj
from omlish.logs.standard import configure_standard_logging

from ...dataserver.server import DataServer
from ...dataserver.targets import DataServerTarget
from ...oci.dataserver import build_oci_repository_data_server_routes
from ..docker.repositories import DockerImageRepositoryOpenerImpl
from ..cache import DataCache
from ..cache import FileCacheDataCache
from ..ci import Ci
from ..docker.buildcaching import DockerBuildCaching
from ..docker.cacheserved import CacheServedDockerCache
from ..docker.cacheserved import build_cache_served_docker_image_data_server_routes
from ..docker.cacheserved import build_cache_served_docker_image_manifest
from ..docker.buildcaching import DockerBuildCachingImpl
from ..docker.dataserver import DockerDataServer
from ..docker.packing import PackedDockerImageIndexRepositoryBuilder
from ..docker.repositories import DockerImageRepositoryOpenerImpl
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

        data_cache = FileCacheDataCache(self.ci_harness.file_cache())

        cs_dc = CacheServedDockerCache(
            image_repo_opener=DockerImageRepositoryOpenerImpl(),
            data_cache=data_cache,
        )

        await cs_dc.save_cache_docker_image(cache_key, image_id)

        with PackedDockerImageIndexRepositoryBuilder(
                image_id=image_id,
        ) as drb:
            built_repo = await drb.build()

            data_server_routes = build_oci_repository_data_server_routes(
                cache_key,
                built_repo,
            )

            async def make_file_cache_key(file_path: str) -> str:
                # FIXME: upload lol
                target_cache_key = f'{cache_key}--{os.path.basename(file_path).split(".")[0]}'
                await data_cache.put_data(
                    target_cache_key,
                    DataCache.FileData(file_path),
                )
                return target_cache_key

            cache_served_manifest = await build_cache_served_docker_image_manifest(
                data_server_routes,
                make_file_cache_key,
            )

        print(json_dumps_pretty(marshal_obj(cache_served_manifest)))

        ####

        port = 5021

        image_url = f'localhost:{port}/{cache_key}'

        print(f'docker run --rm --pull always {image_url} uname -a')

        async def make_cache_key_target(target_cache_key: str, **target_kwargs: ta.Any) -> DataServerTarget:  # noqa
            # FIXME: get cache url lol
            cache_data = check.not_none(await data_cache.get_data(target_cache_key))
            file_path = check.isinstance(cache_data, DataCache.FileData).file_path
            return DataServerTarget.of(
                file_path=file_path,
                **target_kwargs,
            )

        cached_served_data_server_routes = await build_cache_served_docker_image_data_server_routes(
            cache_served_manifest,
            make_cache_key_target,
        )

        data_server = DataServer(DataServer.HandlerRoute.of_(*cached_served_data_server_routes))

        async with DockerDataServer(
                port,
                data_server,
                handler_log=log,
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

                    docker_build_caching=DockerBuildCachingImpl(
                        config=ci_harness.docker_build_caching_impl_config(),

                        docker_cache=CacheServedDockerCache(
                            image_repo_opener=DockerImageRepositoryOpenerImpl(),
                            data_cache=FileCacheDataCache(ci_harness.file_cache()),
                        ),
                    ),

                    docker_image_pulling=ci_harness.docker_image_pulling_impl(),
            ) as ci:
                image_id = await ci.resolve_ci_image()

                print(image_id)

                await asyncio_subprocesses.check_call(
                    'docker',
                    'rmi',
                    image_id,
                )


if __name__ == '__main__':
    asyncio.run(a_main())
