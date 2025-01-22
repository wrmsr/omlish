# ruff: noqa: UP006 UP007
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.os.files import unlinking_if_exists

from ..cache import DirectoryFileCache
from ..cache import FileCache
from .client import GithubCacheClient
from .client import GithubCacheServiceV1Client


##


class GithubFileCache(FileCache):
    def __init__(
            self,
            dir: str,  # noqa
            *,
            client: ta.Optional[GithubCacheClient] = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._dir = check.not_none(dir)

        if client is None:
            client = GithubCacheServiceV1Client(
                cache_version=self._version,
            )
        self._client: GithubCacheClient = client

        self._local = DirectoryFileCache(
            self._dir,
            version=self._version,
        )

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
