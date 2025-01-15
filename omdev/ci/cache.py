# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import os.path
import shlex
import shutil
import typing as ta

from .shell import ShellCmd


##


@abc.abstractmethod
class FileCache(abc.ABC):
    @abc.abstractmethod
    def get_file(self, key: str) -> ta.Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_file(self, key: str) -> ta.Optional[str]:
        raise NotImplementedError


#


class DirectoryFileCache(FileCache):
    def __init__(self, dir: str) -> None:  # noqa
        super().__init__()

        self._dir = dir

    def get_cache_file_path(
            self,
            key: str,
            *,
            make_dirs: bool = False,
    ) -> str:
        if make_dirs:
            os.makedirs(self._dir, exist_ok=True)
        return os.path.join(self._dir, key)

    def get_file(self, key: str) -> ta.Optional[str]:
        cache_file_path = self.get_cache_file_path(key)
        if not os.path.exists(cache_file_path):
            return None
        return cache_file_path

    def put_file(self, file_path: str) -> None:
        key = os.path.basename(file_path)
        cache_file_path = self.get_cache_file_path(key, make_dirs=True)
        shutil.copyfile(file_path, cache_file_path)


##


class ShellCache(abc.ABC):
    @abc.abstractmethod
    def get_file_cmd(self, name: str) -> ta.Optional[ShellCmd]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_file_cmd(self, name: str) -> ShellCmd:
        raise NotImplementedError


#


class DirectoryShellCache(ShellCache):
    def __init__(self, dfc: DirectoryFileCache) -> None:
        super().__init__()

        self._dfc = dfc

    def get_file_cmd(self, key: str) -> ta.Optional[ShellCmd]:
        f = self._dfc.get_file(key)
        if f is None:
            return None
        return ShellCmd(f'cat {shlex.quote(f)}')

    def put_file_cmd(self, key: str) -> ShellCmd:
        f = self._dfc.get_cache_file_path(key, make_dirs=True)
        return ShellCmd(f'cat < {shlex.quote(f)}')
