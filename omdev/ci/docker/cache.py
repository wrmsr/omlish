# ruff: noqa: UP006 UP007
import abc
import typing as ta

from omlish.os.temp import temp_file_context

from ..cache import FileCache
from ..shell import ShellCmd
from .cmds import load_docker_tar_cmd
from .cmds import save_docker_tar_cmd


##


class DockerCache(abc.ABC):
    @abc.abstractmethod
    def load_cache_docker_image(self, key: str) -> ta.Awaitable[ta.Optional[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def save_cache_docker_image(self, key: str, image: str) -> ta.Awaitable[None]:
        raise NotImplementedError


class DockerCacheImpl(DockerCache):
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
