# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.lite.timing import log_timing_context

from ...env import register_github_env_var
from ..clients import BaseGithubCacheClient
from ..clients import GithubCacheClient
from .api import GithubCacheServiceV2
from .api import GithubCacheServiceV2RequestT
from .api import GithubCacheServiceV2ResponseT


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

    async def _send_method_request(
            self,
            method: GithubCacheServiceV2.Method[
                GithubCacheServiceV2RequestT,
                GithubCacheServiceV2ResponseT,
            ],
            request: GithubCacheServiceV2RequestT,
            **kwargs: ta.Any,
    ) -> ta.Optional[GithubCacheServiceV2ResponseT]:
        obj = await self._send_request(
            path=method.name,
            json_content=dc.asdict(request),  # type: ignore[call-overload]
            **kwargs,
        )

        if obj is None:
            return None
        return method.response(**obj)

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        request: GithubCacheServiceV2.GetCacheEntryDownloadUrlRequest
        response: GithubCacheServiceV2.GetCacheEntryDownloadUrlResponse

        def __post_init__(self) -> None:
            check.state(self.response.ok)
            check.non_empty_str(self.response.signed_download_url)

    def get_entry_url(self, entry: GithubCacheClient.Entry) -> ta.Optional[str]:
        entry2 = check.isinstance(entry, self.Entry)
        return check.non_empty_str(entry2.response.signed_download_url)

    #

    async def get_entry(self, key: str) -> ta.Optional[GithubCacheClient.Entry]:
        version = str(self._cache_version).zfill(GithubCacheServiceV2.VERSION_LENGTH)

        req = GithubCacheServiceV2.GetCacheEntryDownloadUrlRequest(
            key=self.fix_key(key),
            restore_keys=[self.fix_key(key, partial_suffix=True)],
            version=version,
        )

        resp = await self._send_method_request(
            GithubCacheServiceV2.GET_CACHE_ENTRY_DOWNLOAD_URL_METHOD,
            req,
        )
        if resp is None or not resp.ok:
            return None

        return self.Entry(
            request=req,
            response=resp,
        )

    #

    async def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        entry2 = check.isinstance(entry, self.Entry)
        with log_timing_context(
                'Downloading github cache '
                f'key {entry2.response.matched_key} '
                f'version {entry2.request.version} '
                f'to {out_file}',
        ):
            await self._download_file(
                check.non_empty_str(entry2.response.matched_key),
                check.non_empty_str(entry2.response.signed_download_url),
                out_file,
            )

    #

    async def upload_file(self, key: str, in_file: str) -> None:
        raise NotImplementedError
