# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.timing import log_timing_context
from omlish.text.mangle import StringMangler

from ..cache import FileCache
from .cache import DockerCache
from .cache import DockerCacheKey
from .cmds import is_docker_image_present
from .cmds import pull_docker_image


##


class DockerImagePulling(abc.ABC):
    @abc.abstractmethod
    def pull_docker_image(self, image: str) -> ta.Awaitable[None]:
        raise NotImplementedError


class DockerImagePullingImpl(DockerImagePulling):
    @dc.dataclass(frozen=True)
    class Config:
        always_pull: bool = False

    def __init__(
            self,
            *,
            config: Config = Config(),

            file_cache: ta.Optional[FileCache] = None,
            docker_cache: ta.Optional[DockerCache] = None,
    ) -> None:
        super().__init__()

        self._config = config

        self._file_cache = file_cache
        self._docker_cache = docker_cache

    async def _pull_docker_image(self, image: str) -> None:
        if not self._config.always_pull and (await is_docker_image_present(image)):
            return

        key_content = StringMangler.of('-', '/:._').mangle(image)

        cache_key = DockerCacheKey(['docker'], key_content)
        if (
                self._docker_cache is not None and
                (await self._docker_cache.load_cache_docker_image(cache_key)) is not None
        ):
            return

        await pull_docker_image(image)

        if self._docker_cache is not None:
            await self._docker_cache.save_cache_docker_image(cache_key, image)

    async def pull_docker_image(self, image: str) -> None:
        with log_timing_context(f'Load docker image: {image}'):
            await self._pull_docker_image(image)
