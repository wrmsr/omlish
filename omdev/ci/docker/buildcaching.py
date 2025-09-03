# ruff: noqa: UP006 UP007 UP045
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract

from .cache import DockerCache
from .cache import DockerCacheKey
from .cmds import is_docker_image_present
from .cmds import tag_docker_image


##


class DockerBuildCaching(Abstract):
    @abc.abstractmethod
    def cached_build_docker_image(
            self,
            cache_key: DockerCacheKey,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],  # image_tag -> image_id
    ) -> ta.Awaitable[str]:
        raise NotImplementedError


class DockerBuildCachingImpl(DockerBuildCaching):
    @dc.dataclass(frozen=True)
    class Config:
        service: str

        always_build: bool = False

    def __init__(
            self,
            *,
            config: Config,

            docker_cache: ta.Optional[DockerCache] = None,
    ) -> None:
        super().__init__()

        self._config = config

        self._docker_cache = docker_cache

    async def cached_build_docker_image(
            self,
            cache_key: DockerCacheKey,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],
    ) -> str:
        image_tag = f'{self._config.service}:{cache_key!s}'

        if not self._config.always_build and (await is_docker_image_present(image_tag)):
            return image_tag

        if (
                self._docker_cache is not None and
                (cache_image_id := await self._docker_cache.load_cache_docker_image(cache_key)) is not None
        ):
            await tag_docker_image(
                cache_image_id,
                image_tag,
            )
            return image_tag

        image_id = await build_and_tag(image_tag)

        if self._docker_cache is not None:
            await self._docker_cache.save_cache_docker_image(cache_key, image_id)

        return image_tag
