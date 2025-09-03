# ruff: noqa: UP006 UP007 UP045
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.os.temp import temp_file_context

from ..cache import FileCache
from ..shell import ShellCmd
from .cmds import load_docker_tar_cmd
from .cmds import save_docker_tar_cmd


##


@dc.dataclass(frozen=True)
class DockerCacheKey:
    prefixes: ta.Sequence[str]
    content: str

    def __post_init__(self) -> None:
        check.not_isinstance(self.prefixes, str)

    def append_prefix(self, *prefixes: str) -> 'DockerCacheKey':
        return dc.replace(self, prefixes=(*self.prefixes, *prefixes))

    SEPARATOR: ta.ClassVar[str] = '--'

    def __str__(self) -> str:
        return self.SEPARATOR.join([*self.prefixes, self.content])


##


class DockerCache(Abstract):
    @abc.abstractmethod
    def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Awaitable[ta.Optional[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> ta.Awaitable[None]:
        raise NotImplementedError


class DockerCacheImpl(DockerCache):
    def __init__(
            self,
            *,
            file_cache: ta.Optional[FileCache] = None,
    ) -> None:
        super().__init__()

        self._file_cache = file_cache

    async def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Optional[str]:
        if self._file_cache is None:
            return None

        cache_file = await self._file_cache.get_file(str(key))
        if cache_file is None:
            return None

        get_cache_cmd = ShellCmd(f'cat {cache_file} | zstd -cd --long')

        return await load_docker_tar_cmd(get_cache_cmd)

    async def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> None:
        if self._file_cache is None:
            return

        with temp_file_context() as tmp_file:
            write_tmp_cmd = ShellCmd(f'zstd > {tmp_file}')

            await save_docker_tar_cmd(image, write_tmp_cmd)

            await self._file_cache.put_file(str(key), tmp_file, steal=True)
