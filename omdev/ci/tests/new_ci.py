# ruff: noqa: PT009 UP006 UP007
import asyncio
import dataclasses as dc

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.logs.standard import configure_standard_logging

from ..cache import FileCacheDataCache
from ..ci import Ci
from ..docker.buildcaching import DockerBuildCachingImpl
from ..docker.cacheserved.cache import CacheServedDockerCache
from ..docker.repositories import DockerImageRepositoryOpenerImpl
from .harness import CiHarness


##


async def a_main() -> None:
    configure_standard_logging('DEBUG')

    async with CiHarness() as ci_harness:
        for _ in range(2):
            async with Ci(
                    config=dc.replace(
                        ci_harness.ci_config(),

                        setup_concurrency=2,
                    ),

                    docker_build_caching=DockerBuildCachingImpl(
                        config=ci_harness.docker_build_caching_impl_config(),

                        docker_cache=CacheServedDockerCache(
                            image_repo_opener=DockerImageRepositoryOpenerImpl(),
                            data_cache=FileCacheDataCache(ci_harness.file_cache()),
                        ),
                    ),

                    docker_image_pulling=ci_harness.docker_image_pulling_impl(),
            ) as ci:
                image_id = await ci.resolve_ci_image_task()

                print(image_id)

                await asyncio_subprocesses.check_call(
                    'docker',
                    'rmi',
                    image_id,
                )


if __name__ == '__main__':
    asyncio.run(a_main())
