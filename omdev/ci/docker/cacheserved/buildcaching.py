# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from ..buildcaching import DockerBuildCaching
from ..cache import DockerCache
from ..cmds import is_docker_image_present


##


class NewDockerBuildCaching(DockerBuildCaching):
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
            cache_key: str,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],
    ) -> str:
        image_tag = f'{self._config.service}:{cache_key}'

        if not self._config.always_build and (await is_docker_image_present(image_tag)):
            return image_tag

        raise NotImplementedError
