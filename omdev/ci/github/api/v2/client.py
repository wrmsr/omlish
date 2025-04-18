# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.check import check

from ...env import register_github_env_var
from ..clients import BaseGithubCacheClient
from ..clients import GithubCacheClient
from .api import GithubCacheServiceV2


##


class GithubCacheServiceV2Client(BaseGithubCacheClient):
    BASE_URL_ENV_VAR = register_github_env_var('ACTIONS_RESULTS_URL')

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> None:
        if base_url is None:
            base_url = check.non_empty_str(self.BASE_URL_ENV_VAR())
        service_url = GithubCacheServiceV2.get_service_url(base_url)

        super().__init__(
            service_url=service_url,
            **kwargs,
        )

    #

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
