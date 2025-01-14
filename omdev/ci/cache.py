# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import os.path
import shutil
import typing as ta


#


@abc.abstractmethod
class FileCache(abc.ABC):
    @abc.abstractmethod
    def get_file(self, name: str) -> ta.Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_file(self, name: str) -> ta.Optional[str]:
        raise NotImplementedError


#


class DirectoryFileCache(FileCache):
    def __init__(self, dir: str) -> None:  # noqa
        super().__init__()

        self._dir = dir

    def get_file(self, name: str) -> ta.Optional[str]:
        file_path = os.path.join(self._dir, name)
        if not os.path.exists(file_path):
            return None
        return file_path

    def put_file(self, file_path: str) -> None:
        os.makedirs(self._dir, exist_ok=True)
        cache_file_path = os.path.join(self._dir, os.path.basename(file_path))
        shutil.copyfile(file_path, cache_file_path)
