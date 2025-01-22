# ruff: noqa: UP006 UP007
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import AsyncExitStacked
from omlish.os.temp import temp_file_context

from .cache import FileCache
from .compose import DockerComposeRun
from .compose import get_compose_service_dependencies
from .docker import build_docker_file_hash
from .docker import build_docker_image
from .docker import is_docker_image_present
from .docker import load_docker_tar_cmd
from .docker import pull_docker_image
from .docker import save_docker_tar_cmd
from .docker import tag_docker_image
from .requirements import build_requirements_hash
from .shell import ShellCmd
from .utils import log_timing_context


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

        no_dependencies: bool = False

        run_options: ta.Optional[ta.Sequence[str]] = None

        #

        def __post_init__(self) -> None:
            check.not_isinstance(self.requirements_txts, str)

    def __init__(
            self,
            cfg: Config,
            *,
            file_cache: ta.Optional[FileCache] = None,
    ) -> None:
        super().__init__()

        self._cfg = cfg
        self._file_cache = file_cache

    #

    async def _load_docker_image(self, image: str) -> None:
        if not self._cfg.always_pull and (await is_docker_image_present(image)):
            return

        dep_suffix = image
        for c in '/:.-_':
            dep_suffix = dep_suffix.replace(c, '-')

        cache_key = f'docker-{dep_suffix}'
        if (await self._load_cache_docker_image(cache_key)) is not None:
            return

        await pull_docker_image(image)

        await self._save_cache_docker_image(cache_key, image)

    async def load_docker_image(self, image: str) -> None:
        with log_timing_context(f'Load docker image: {image}'):
            await self._load_docker_image(image)

    #

    async def _load_cache_docker_image(self, key: str) -> ta.Optional[str]:
        if self._file_cache is None:
            return None

        cache_file = await self._file_cache.get_file(key)
        if cache_file is None:
            return None

        get_cache_cmd = ShellCmd(f'cat {cache_file} | zstd -cd --long')

        return await load_docker_tar_cmd(get_cache_cmd)

    async def _save_cache_docker_image(self, key: str, image: str) -> None:
        if self._file_cache is None:
            return

        with temp_file_context() as tmp_file:
            write_tmp_cmd = ShellCmd(f'zstd > {tmp_file}')

            await save_docker_tar_cmd(image, write_tmp_cmd)

            await self._file_cache.put_file(key, tmp_file, steal=True)

    #

    async def _resolve_docker_image(
            self,
            cache_key: str,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],
    ) -> str:
        image_tag = f'{self._cfg.service}:{cache_key}'

        if not self._cfg.always_build and (await is_docker_image_present(image_tag)):
            return image_tag

        if (cache_image_id := await self._load_cache_docker_image(cache_key)) is not None:
            await tag_docker_image(
                cache_image_id,
                image_tag,
            )
            return image_tag

        image_id = await build_and_tag(image_tag)

        await self._save_cache_docker_image(cache_key, image_id)

        return image_tag

    #

    @cached_nullary
    def docker_file_hash(self) -> str:
        return build_docker_file_hash(self._cfg.docker_file)[:self.KEY_HASH_LEN]

    async def _resolve_ci_base_image(self) -> str:
        async def build_and_tag(image_tag: str) -> str:
            return await build_docker_image(
                self._cfg.docker_file,
                tag=image_tag,
                cwd=self._cfg.project_dir,
            )

        cache_key = f'ci-base-{self.docker_file_hash()}'

        return await self._resolve_docker_image(cache_key, build_and_tag)

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
            os.path.join(self._cfg.project_dir, rf)
            for rf in check.not_none(self._cfg.requirements_txts)
        ]

    @cached_nullary
    def requirements_hash(self) -> str:
        return build_requirements_hash(self.requirements_txts())[:self.KEY_HASH_LEN]

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
                    *[f'-r /project/{rf}' for rf in self._cfg.requirements_txts or []],
                ]),
            ]
            setup_cmd = ' && '.join(setup_cmds)

            docker_file_lines = [
                f'FROM {base_image}',
                'RUN mkdir /project',
                *[f'COPY {rf} /project/{rf}' for rf in self._cfg.requirements_txts or []],
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
                    cwd=self._cfg.project_dir,
                )

        cache_key = f'ci-{self.docker_file_hash()}-{self.requirements_hash()}'

        return await self._resolve_docker_image(cache_key, build_and_tag)

    @async_cached_nullary
    async def resolve_ci_image(self) -> str:
        with log_timing_context('Resolve ci image') as ltc:
            image_id = await self._resolve_ci_image()
            ltc.set_description(f'Resolve ci image: {image_id}')
            return image_id

    #

    @async_cached_nullary
    async def load_dependencies(self) -> None:
        deps = get_compose_service_dependencies(
            self._cfg.compose_file,
            self._cfg.service,
        )

        for dep_image in deps.values():
            await self.load_docker_image(dep_image)

    #

    async def _run_compose_(self) -> None:
        async with DockerComposeRun(DockerComposeRun.Config(
            compose_file=self._cfg.compose_file,
            service=self._cfg.service,

            image=await self.resolve_ci_image(),

            cmd=self._cfg.cmd,

            run_options=[
                '-v', f'{os.path.abspath(self._cfg.project_dir)}:/project',
                *(self._cfg.run_options or []),
            ],

            cwd=self._cfg.project_dir,

            no_dependencies=self._cfg.no_dependencies,
        )) as ci_compose_run:
            await ci_compose_run.run()

    async def _run_compose(self) -> None:
        with log_timing_context('Run compose'):
            await self._run_compose_()

    #

    async def run(self) -> None:
        await self.resolve_ci_image()

        await self.load_dependencies()

        await self._run_compose()
