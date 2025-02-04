# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import async_cached_nullary
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import AsyncExitStacked
from omlish.os.temp import temp_file_context

from ..cache import FileCache
from ..compose import DockerComposeRun
from ..compose import get_compose_service_dependencies
from .utils import build_docker_file_hash
from .utils import build_docker_image
from .utils import is_docker_image_present
from .utils import load_docker_tar_cmd
from .utils import pull_docker_image
from .utils import save_docker_tar_cmd
from .utils import tag_docker_image
from ..requirements import build_requirements_hash
from ..shell import ShellCmd
from ..utils import log_timing_context


##


class CiDockerCache(abc.ABC):
    @abc.abstractmethod
    def load_cache_docker_image(self, key: str) -> ta.Awaitable[ta.Optional[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def save_cache_docker_image(self, key: str, image: str) -> ta.Awaitable[None]:
        raise NotImplementedError


class CiDockerCacheImpl(CiDockerCache):
    def __init__(
            self,
            *,
            file_cache: ta.Optional[FileCache] = None,
    ) -> None:
        super().__init__()

        self._file_cache = file_cache

    async def load_cache_docker_image(self, key: str) -> ta.Optional[str]:
        if self._file_cache is None:
            return None

        cache_file = await self._file_cache.get_file(key)
        if cache_file is None:
            return None

        get_cache_cmd = ShellCmd(f'cat {cache_file} | zstd -cd --long')

        return await load_docker_tar_cmd(get_cache_cmd)

    async def save_cache_docker_image(self, key: str, image: str) -> None:
        if self._file_cache is None:
            return

        with temp_file_context() as tmp_file:
            write_tmp_cmd = ShellCmd(f'zstd > {tmp_file}')

            await save_docker_tar_cmd(image, write_tmp_cmd)

            await self._file_cache.put_file(key, tmp_file, steal=True)

