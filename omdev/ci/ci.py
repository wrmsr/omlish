# ruff: noqa: UP006 UP007
import dataclasses as dc
import functools
import os.path
import typing as ta

from omlish.asyncs.asyncio.utils import asyncio_wait_maybe_concurrent
from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import AsyncExitStacked
from omlish.lite.timing import log_timing_context
from omlish.os.temp import temp_file_context

from .compose import DockerComposeRun
from .compose import get_compose_service_dependencies
from .docker.buildcaching import DockerBuildCaching
from .docker.cache import DockerCacheKey
from .docker.cmds import build_docker_image
from .docker.cmds import ensure_docker_image_setup
from .docker.imagepulling import DockerImagePulling
from .docker.utils import build_docker_file_hash
from .requirements import build_requirements_hash
from .shell import ShellCmd


##


class Ci(AsyncExitStacked):
    KEY_HASH_LEN = 16

    @dc.dataclass(frozen=True)
    class Config:
        project_dir: str

        docker_file: str

        compose_file: str
        service: str

        cmd: ShellCmd

        #

        requirements_txts: ta.Optional[ta.Sequence[str]] = None

        always_pull: bool = False
        always_build: bool = False

        setup_concurrency: ta.Optional[int] = None

        no_dependencies: bool = False

        setup_only: bool = False

        run_options: ta.Optional[ta.Sequence[str]] = None

        #

        def __post_init__(self) -> None:
            check.not_isinstance(self.requirements_txts, str)

    def __init__(
            self,
            config: Config,
            *,
            docker_build_caching: DockerBuildCaching,
            docker_image_pulling: DockerImagePulling,
    ) -> None:
        super().__init__()

        self._config = config

        self._docker_build_caching = docker_build_caching
        self._docker_image_pulling = docker_image_pulling

    #

    @cached_nullary
    def docker_file_hash(self) -> str:
        return build_docker_file_hash(self._config.docker_file)[:self.KEY_HASH_LEN]

    @cached_nullary
    def ci_base_image_cache_key(self) -> DockerCacheKey:
        return DockerCacheKey(['ci-base'], self.docker_file_hash())

    async def _resolve_ci_base_image(self) -> str:
        async def build_and_tag(image_tag: str) -> str:
            return await build_docker_image(
                self._config.docker_file,
                tag=image_tag,
                cwd=self._config.project_dir,
            )

        return await self._docker_build_caching.cached_build_docker_image(
            self.ci_base_image_cache_key(),
            build_and_tag,
        )

    @async_cached_nullary
    async def resolve_ci_base_image(self) -> str:
        with log_timing_context('Resolve ci base image') as ltc:
            image_id = await self._resolve_ci_base_image()
            ltc.set_description(f'Resolve ci base image: {image_id}')
            return image_id

    #

    @cached_nullary
    def requirements_txts(self) -> ta.Sequence[str]:
        return [
            os.path.join(self._config.project_dir, rf)
            for rf in check.not_none(self._config.requirements_txts)
        ]

    @cached_nullary
    def requirements_hash(self) -> str:
        return build_requirements_hash(self.requirements_txts())[:self.KEY_HASH_LEN]

    @cached_nullary
    def ci_image_cache_key(self) -> DockerCacheKey:
        return DockerCacheKey(['ci'], f'{self.docker_file_hash()}-{self.requirements_hash()}')

    async def _resolve_ci_image(self) -> str:
        async def build_and_tag(image_tag: str) -> str:
            base_image = await self.resolve_ci_base_image()

            setup_cmds = [
                ' '.join([
                    'pip install',
                    '--no-cache-dir',
                    '--root-user-action ignore',
                    'uv',
                ]),
                ' '.join([
                    'uv pip install',
                    '--no-cache',
                    '--index-strategy unsafe-best-match',
                    '--system',
                    *[f'-r /project/{rf}' for rf in self._config.requirements_txts or []],
                ]),
            ]
            setup_cmd = ' && '.join(setup_cmds)

            docker_file_lines = [
                f'FROM {base_image}',
                'RUN mkdir /project',
                *[f'COPY {rf} /project/{rf}' for rf in self._config.requirements_txts or []],
                f'RUN {setup_cmd}',
                'RUN rm /project/*',
                'WORKDIR /project',
            ]

            with temp_file_context() as docker_file:
                with open(docker_file, 'w') as f:  # noqa
                    f.write('\n'.join(docker_file_lines))

                return await build_docker_image(
                    docker_file,
                    tag=image_tag,
                    cwd=self._config.project_dir,
                )

        return await self._docker_build_caching.cached_build_docker_image(
            self.ci_image_cache_key(),
            build_and_tag,
        )

    @async_cached_nullary
    async def resolve_ci_image(self) -> str:
        with log_timing_context('Resolve ci image') as ltc:
            image_id = await self._resolve_ci_image()
            ltc.set_description(f'Resolve ci image: {image_id}')
            return image_id

    #

    @cached_nullary
    def get_dependency_images(self) -> ta.Sequence[str]:
        deps = get_compose_service_dependencies(
            self._config.compose_file,
            self._config.service,
        )
        return sorted(deps.values())

    @cached_nullary
    def pull_dependencies_funcs(self) -> ta.Sequence[ta.Callable[[], ta.Awaitable]]:
        return [
            async_cached_nullary(functools.partial(
                self._docker_image_pulling.pull_docker_image,
                dep_image,
            ))
            for dep_image in self.get_dependency_images()
        ]

    #

    @cached_nullary
    def setup_funcs(self) -> ta.Sequence[ta.Callable[[], ta.Awaitable]]:
        return [
            self.resolve_ci_image,

            *(self.pull_dependencies_funcs() if not self._config.no_dependencies else []),
        ]

    @async_cached_nullary
    async def setup(self) -> None:
        await asyncio_wait_maybe_concurrent(
            [fn() for fn in self.setup_funcs()],
            self._config.setup_concurrency,
        )

    #

    async def _run_compose_(self) -> None:
        async with DockerComposeRun(DockerComposeRun.Config(
            compose_file=self._config.compose_file,
            service=self._config.service,

            image=await self.resolve_ci_image(),

            cmd=self._config.cmd,

            run_options=[
                '-v', f'{os.path.abspath(self._config.project_dir)}:/project',
                *(self._config.run_options or []),
            ],

            cwd=self._config.project_dir,

            no_dependencies=self._config.no_dependencies,
        )) as ci_compose_run:
            await ci_compose_run.run()

    async def _run_compose(self) -> None:
        with log_timing_context('Run compose'):
            await self._run_compose_()

    #

    async def _run_setup_only(self) -> None:
        image_ids = [
            await self.resolve_ci_image(),

            *(self.get_dependency_images() if not self._config.no_dependencies else []),
        ]

        for image_id in image_ids:
            with log_timing_context(f'Run setup only: {image_id}'):
                await ensure_docker_image_setup(
                    image_id,
                    cwd=self._config.project_dir,
                )

    #

    async def run(self) -> None:
        await self.setup()

        if self._config.setup_only:
            await self._run_setup_only()
        else:
            await self._run_compose()
