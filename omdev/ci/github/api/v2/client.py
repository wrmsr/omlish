# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from ..clients import GithubCacheClient


##


class GithubCacheServiceV2Client(GithubCacheClient):
    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        pass

    @abc.abstractmethod
    def get_entry(self, key: str) -> ta.Awaitable[ta.Optional[GithubCacheClient.Entry]]:
        raise NotImplementedError

    def get_entry_url(self, entry: GithubCacheClient.Entry) -> ta.Optional[str]:
        return None

    @abc.abstractmethod
    def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, key: str, in_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError
