# ruff: noqa: UP006 UP007 UP045
"""
TODO:
 - os.mtime, Config.purge_after_days
  - nice to have: get a total set of might-need keys ahead of time and keep those
  - okay: just purge after running
"""
import abc
import asyncio
import dataclasses as dc
import functools
import os.path
import shutil
import time
import typing as ta
import urllib.request

from omlish.lite.abstract import Abstract
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.logs.modules import get_module_logger
from omlish.os.temp import make_temp_file

from .consts import CI_CACHE_VERSION


CacheVersion = ta.NewType('CacheVersion', int)


log = get_module_logger(globals())  # noqa


##


class FileCache(Abstract):
    DEFAULT_CACHE_VERSION: ta.ClassVar[CacheVersion] = CacheVersion(CI_CACHE_VERSION)

    def __init__(
            self,
            *,
            version: ta.Optional[CacheVersion] = None,
    ) -> None:
        super().__init__()

        if version is None:
            version = self.DEFAULT_CACHE_VERSION
        check.isinstance(version, int)
        check.arg(version >= 0)
        self._version: CacheVersion = version

    @property
    def version(self) -> CacheVersion:
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
    @dc.dataclass(frozen=True)
    class Config:
        dir: str

        no_create: bool = False
        no_purge: bool = False

        no_update_mtime: bool = False

        purge_max_age_s: ta.Optional[float] = None
        purge_max_size_b: ta.Optional[int] = None

    def __init__(
            self,
            config: Config,
            *,
            version: ta.Optional[CacheVersion] = None,
    ) -> None:  # noqa
        super().__init__(
            version=version,
        )

        self._config = config

    @property
    def dir(self) -> str:
        return self._config.dir

    #

    VERSION_FILE_NAME = '.ci-cache-version'

    def _iter_dir_contents(self) -> ta.Iterator[str]:
        for n in sorted(os.listdir(self.dir)):
            if n.startswith('.'):
                continue
            yield os.path.join(self.dir, n)

    @cached_nullary
    def setup_dir(self) -> None:
        version_file = os.path.join(self.dir, self.VERSION_FILE_NAME)

        if self._config.no_create:
            check.state(os.path.isdir(self.dir))

        elif not os.path.isdir(self.dir):
            os.makedirs(self.dir)
            with open(version_file, 'w') as f:
                f.write(f'{self._version}\n')
            return

        # NOTE: intentionally raises FileNotFoundError to refuse to use an existing non-cache dir as a cache dir.
        with open(version_file) as f:
            dir_version = int(f.read().strip())

        if dir_version == self._version:
            return

        if self._config.no_purge:
            raise RuntimeError(f'{dir_version=} != {self._version=}')

        dirs = [n for n in sorted(os.listdir(self.dir)) if os.path.isdir(os.path.join(self.dir, n))]
        if dirs:
            raise RuntimeError(
                f'Refusing to remove stale cache dir {self.dir!r} '
                f'due to present directories: {", ".join(dirs)}',
            )

        for fp in self._iter_dir_contents():
            check.state(os.path.isfile(fp))
            log.debug('Purging stale cache file: %s', fp)
            os.unlink(fp)

        os.unlink(version_file)

        with open(version_file, 'w') as f:
            f.write(str(self._version))

    #

    def purge(self, *, dry_run: bool = False) -> None:
        purge_max_age_s = self._config.purge_max_age_s
        purge_max_size_b = self._config.purge_max_size_b
        if self._config.no_purge or (purge_max_age_s is None and purge_max_size_b is None):
            return

        self.setup_dir()

        purge_min_mtime: ta.Optional[float] = None
        if purge_max_age_s is not None:
            purge_min_mtime = time.time() - purge_max_age_s

        dct: ta.Dict[str, os.stat_result] = {}
        for fp in self._iter_dir_contents():
            check.state(os.path.isfile(fp))
            dct[fp] = os.stat(fp)

        total_size_b = 0
        for fp, st in sorted(dct.items(), key=lambda t: -t[1].st_mtime):
            total_size_b += st.st_size

            purge = False
            if purge_min_mtime is not None and st.st_mtime < purge_min_mtime:
                purge = True
            if purge_max_size_b is not None and total_size_b >= purge_max_size_b:
                purge = True

            if not purge:
                continue

            log.debug('Purging cache file: %s', fp)
            if not dry_run:
                os.unlink(fp)

    #

    def get_cache_file_path(
            self,
            key: str,
    ) -> str:
        self.setup_dir()
        return os.path.join(self.dir, key)

    def format_incomplete_file(self, f: str) -> str:
        return os.path.join(os.path.dirname(f), f'_{os.path.basename(f)}.incomplete')

    #

    async def get_file(self, key: str) -> ta.Optional[str]:
        cache_file_path = self.get_cache_file_path(key)
        if not os.path.exists(cache_file_path):
            return None

        if not self._config.no_update_mtime:
            stat_info = os.stat(cache_file_path)
            os.utime(cache_file_path, (stat_info.st_atime, time.time()))

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


##


class DataCache:
    @dc.dataclass(frozen=True)
    class Data(Abstract):
        pass

    @dc.dataclass(frozen=True)
    class BytesData(Data):
        data: bytes

    @dc.dataclass(frozen=True)
    class FileData(Data):
        file_path: str

    @dc.dataclass(frozen=True)
    class UrlData(Data):
        url: str

    #

    @abc.abstractmethod
    def get_data(self, key: str) -> ta.Awaitable[ta.Optional[Data]]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_data(self, key: str, data: Data) -> ta.Awaitable[None]:
        raise NotImplementedError


#


@functools.singledispatch
async def read_data_cache_data(data: DataCache.Data) -> bytes:
    raise TypeError(data)


@read_data_cache_data.register
async def _(data: DataCache.BytesData) -> bytes:
    return data.data


@read_data_cache_data.register
async def _(data: DataCache.FileData) -> bytes:
    with open(data.file_path, 'rb') as f:  # noqa
        return f.read()


@read_data_cache_data.register
async def _(data: DataCache.UrlData) -> bytes:
    def inner() -> bytes:
        with urllib.request.urlopen(urllib.request.Request(  # noqa
            data.url,
        )) as resp:
            return resp.read()

    return await asyncio.get_running_loop().run_in_executor(None, inner)


#


class FileCacheDataCache(DataCache):
    def __init__(
            self,
            file_cache: FileCache,
    ) -> None:
        super().__init__()

        self._file_cache = file_cache

    async def get_data(self, key: str) -> ta.Optional[DataCache.Data]:
        if (file_path := await self._file_cache.get_file(key)) is None:
            return None

        return DataCache.FileData(file_path)

    async def put_data(self, key: str, data: DataCache.Data) -> None:
        steal = False

        if isinstance(data, DataCache.BytesData):
            file_path = make_temp_file()
            with open(file_path, 'wb') as f:  # noqa
                f.write(data.data)
            steal = True

        elif isinstance(data, DataCache.FileData):
            file_path = data.file_path

        elif isinstance(data, DataCache.UrlData):
            raise NotImplementedError

        else:
            raise TypeError(data)

        await self._file_cache.put_file(
            key,
            file_path,
            steal=steal,
        )
