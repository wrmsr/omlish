# ruff: noqa: PT009
import contextlib
import datetime
import os.path
import shlex
import shutil
import unittest

from omlish.os.temp import temp_dir_context

from ..cache import DirectoryFileCache
from ..ci import Ci
from ..docker.buildcaching import DockerBuildCachingImpl
from ..docker.cache import DockerCacheImpl
from ..docker.imagepulling import DockerImagePullingImpl
from ..shell import ShellCmd


class TestCi(unittest.IsolatedAsyncioTestCase):
    async def test_ci(self):
        async with contextlib.AsyncExitStack() as es:
            self_dir = os.path.dirname(__file__)
            self_project_dir = os.path.join(self_dir, 'project')

            temp_dir: str = es.enter_context(temp_dir_context())  # noqa
            temp_project_dir = os.path.join(temp_dir, 'project')
            shutil.copytree(self_project_dir, temp_project_dir)

            now_str = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            docker_file = os.path.join(temp_project_dir, 'Dockerfile')
            with open(docker_file) as f:  # noqa
                docker_file_src = f.read()
            docker_file_src += f'\nRUN echo {shlex.quote(now_str)} > /.timestamp\n'
            with open(docker_file, 'w') as f:  # noqa
                f.write(docker_file_src)

            cache_dir = os.path.join(temp_dir, 'cache')

            config = Ci.Config(
                project_dir=temp_project_dir,

                docker_file=os.path.join(temp_project_dir, 'Dockerfile'),

                compose_file=os.path.join(temp_project_dir, 'compose.yml'),
                service='omlish-ci',

                cmd=ShellCmd('true'),

                requirements_txts=[
                    'requirements-dev.txt',
                    'requirements.txt',
                ],
            )

            file_cache = DirectoryFileCache(DirectoryFileCache.Config(
                dir=cache_dir,
            ))

            docker_cache = DockerCacheImpl(
                file_cache=file_cache,
            )

            docker_image_pulling = DockerImagePullingImpl(
                config=DockerImagePullingImpl.Config(
                    always_pull=config.always_pull,
                ),

                file_cache=file_cache,
                docker_cache=docker_cache,
            )

            docker_build_caching = DockerBuildCachingImpl(
                config=DockerBuildCachingImpl.Config(
                    service=config.service,

                    always_build=config.always_build,
                ),

                docker_cache=docker_cache,
            )

            async with Ci(
                    config,

                    file_cache=file_cache,

                    docker_build_caching=docker_build_caching,
                    docker_image_pulling=docker_image_pulling,
            ) as ci:
                await ci.run()
