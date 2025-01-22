# ruff: noqa: UP006 UP007
import abc
import os.path
import shutil
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.logs import log

from .consts import CI_CACHE_VERSION


##


@abc.abstractmethod
class FileCache(abc.ABC):
    def __init__(
            self,
            *,
            version: int = CI_CACHE_VERSION,
    ) -> None:
        super().__init__()

        check.isinstance(version, int)
        check.arg(version >= 0)
        self._version = version

    @property
    def version(self) -> int:
        return self._version

    #

    @abc.abstractmethod
    def get_file(self, key: str) -> ta.Awaitable[ta.Optional[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> ta.Awaitable[str]:
        raise NotImplementedError


#


class DirectoryFileCache(FileCache):
    def __init__(
            self,
            dir: str,  # noqa
            *,
            no_create: bool = False,
            no_purge: bool = False,
            **kwargs: ta.Any,
    ) -> None:  # noqa
        super().__init__(**kwargs)

        self._dir = dir
        self._no_create = no_create
        self._no_purge = no_purge

    #

    VERSION_FILE_NAME = '.ci-cache-version'

    @cached_nullary
    def setup_dir(self) -> None:
        version_file = os.path.join(self._dir, self.VERSION_FILE_NAME)

        if self._no_create:
            check.state(os.path.isdir(self._dir))

        elif not os.path.isdir(self._dir):
            os.makedirs(self._dir)
            with open(version_file, 'w') as f:
                f.write(str(self._version))
            return

        with open(version_file) as f:
            dir_version = int(f.read().strip())

        if dir_version == self._version:
            return

        if self._no_purge:
            raise RuntimeError(f'{dir_version=} != {self._version=}')

        dirs = [n for n in sorted(os.listdir(self._dir)) if os.path.isdir(os.path.join(self._dir, n))]
        if dirs:
            raise RuntimeError(
                f'Refusing to remove stale cache dir {self._dir!r} '
                f'due to present directories: {", ".join(dirs)}',
            )

        for n in sorted(os.listdir(self._dir)):
            if n.startswith('.'):
                continue
            fp = os.path.join(self._dir, n)
            check.state(os.path.isfile(fp))
            log.debug('Purging stale cache file: %s', fp)
            os.unlink(fp)

        os.unlink(version_file)

        with open(version_file, 'w') as f:
            f.write(str(self._version))

    #

    def get_cache_file_path(
            self,
            key: str,
    ) -> str:
        self.setup_dir()
        return os.path.join(self._dir, key)

    def format_incomplete_file(self, f: str) -> str:
        return os.path.join(os.path.dirname(f), f'_{os.path.basename(f)}.incomplete')

    #

    async def get_file(self, key: str) -> ta.Optional[str]:
        cache_file_path = self.get_cache_file_path(key)
        if not os.path.exists(cache_file_path):
            return None
        return cache_file_path

    async def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> str:
        cache_file_path = self.get_cache_file_path(key)
        if steal:
            shutil.move(file_path, cache_file_path)
        else:
            shutil.copyfile(file_path, cache_file_path)
        return cache_file_path
