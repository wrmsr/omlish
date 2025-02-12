# ruff: noqa: UP006 UP007
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.os.files import unlinking_if_exists

from ..cache import CacheVersion
from ..cache import DataCache
from ..cache import DirectoryFileCache
from ..cache import FileCache
from ..cache import FileCacheDataCache
from .client import GithubCacheClient
from .client import GithubCacheServiceV1Client


##


class GithubCache(FileCache, DataCache):
    @dc.dataclass(frozen=True)
    class Config:
        pass

    def __init__(
            self,
            config: Config = Config(),
            *,
            client: ta.Optional[GithubCacheClient] = None,
            version: ta.Optional[CacheVersion] = None,

            local: DirectoryFileCache,
    ) -> None:
        super().__init__(
            version=version,
        )

        self._config = config

        if client is None:
            client = GithubCacheServiceV1Client(
                cache_version=self._version,
            )
        self._client: GithubCacheClient = client

        self._local = local

    #

    async def get_file(self, key: str) -> ta.Optional[str]:
        local_file = self._local.get_cache_file_path(key)
        if os.path.exists(local_file):
            return local_file

        if (entry := await self._client.get_entry(key)) is None:
            return None

        tmp_file = self._local.format_incomplete_file(local_file)
        with unlinking_if_exists(tmp_file):
            await self._client.download_file(entry, tmp_file)

            os.replace(tmp_file, local_file)

        return local_file

    async def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> str:
        cache_file_path = await self._local.put_file(
            key,
            file_path,
            steal=steal,
        )

        await self._client.upload_file(key, cache_file_path)

        return cache_file_path

    #

    async def get_data(self, key: str) -> ta.Optional[DataCache.Data]:
        local_file = self._local.get_cache_file_path(key)
        if os.path.exists(local_file):
            return DataCache.FileData(local_file)

        if (entry := await self._client.get_entry(key)) is None:
            return None

        return DataCache.UrlData(check.non_empty_str(self._client.get_entry_url(entry)))

    async def put_data(self, key: str, data: DataCache.Data) -> None:
        await FileCacheDataCache(self).put_data(key, data)
