# ruff: noqa: PT009 UP006 UP007
import datetime
import os.path
import shlex
import shutil

from omlish.lite.cached import cached_nullary
from omlish.lite.contextmanagers import AsyncExitStacked
from omlish.os.temp import temp_dir_context

from ..cache import DirectoryFileCache
from ..cache import FileCache
from ..ci import Ci
from ..docker.buildcaching import DockerBuildCachingImpl
from ..docker.cache import DockerCacheImpl
from ..docker.imagepulling import DockerImagePullingImpl
from ..shell import ShellCmd


class CiHarness(AsyncExitStacked):
    @cached_nullary
    def self_dir(self) -> str:
        return os.path.dirname(__file__)

    @cached_nullary
    def self_project_dir(self) -> str:
        return os.path.join(self.self_dir(), 'project')

    #

    @cached_nullary
    def temp_dir(self) -> str:
        return self._enter_context(temp_dir_context())  # noqa

    @cached_nullary
    def temp_project_dir(self) -> str:
        temp_project_dir = os.path.join(self.temp_dir(), 'project')
        shutil.copytree(self.self_project_dir(), temp_project_dir)
        return temp_project_dir

    #

    @cached_nullary
    def now_str(self) -> str:
        return datetime.datetime.now(tz=datetime.timezone.utc).isoformat()  # noqa

    #

    @cached_nullary
    def docker_file(self) -> str:
        docker_file = os.path.join(self.temp_project_dir(), 'Dockerfile')
        with open(docker_file) as f:  # noqa
            docker_file_src = f.read()
        docker_file_src += f'\nRUN echo {shlex.quote(self.now_str())} > /.timestamp\n'
        with open(docker_file, 'w') as f:  # noqa
            f.write(docker_file_src)
        return docker_file

    #

    @cached_nullary
    def cache_dir(self) -> str:
        return os.path.join(self.temp_dir(), 'cache')

    #

    @cached_nullary
    def ci_config(self) -> Ci.Config:
        return Ci.Config(
            project_dir=self.temp_project_dir(),

            docker_file=self.docker_file(),

            compose_file=os.path.join(self.temp_project_dir(), 'compose.yml'),
            service='omlish-ci',

            cmd=ShellCmd('cat /.timestamp'),

            requirements_txts=[
                'requirements-dev.txt',
                'requirements.txt',
            ],
        )

    #

    @cached_nullary
    def directory_file_cache(self) -> DirectoryFileCache:
        return DirectoryFileCache(DirectoryFileCache.Config(
            dir=self.cache_dir(),
        ))

    @cached_nullary
    def file_cache(self) -> FileCache:
        return self.directory_file_cache()

    #

    @cached_nullary
    def docker_cache_impl(self) -> DockerCacheImpl:
        return DockerCacheImpl(
            file_cache=self.file_cache(),
        )

    @cached_nullary
    def docker_image_pulling_impl(self) -> DockerImagePullingImpl:
        return DockerImagePullingImpl(
            config=DockerImagePullingImpl.Config(
                always_pull=self.ci_config().always_pull,
            ),

            file_cache=self.file_cache(),
            docker_cache=self.docker_cache_impl(),
        )

    @cached_nullary
    def docker_build_caching_impl(self) -> DockerBuildCachingImpl:
        return DockerBuildCachingImpl(
            config=DockerBuildCachingImpl.Config(
                service=self.ci_config().service,

                always_build=self.ci_config().always_build,
            ),

            docker_cache=self.docker_cache_impl(),
        )

    #

    def make_ci(self) -> Ci:
        return Ci(
            self.ci_config(),

            docker_build_caching=self.docker_build_caching_impl(),
            docker_image_pulling=self.docker_image_pulling_impl(),
        )
