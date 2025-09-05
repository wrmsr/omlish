# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc
import os
import typing as ta
import urllib.request

from omlish.lite.check import check
from omlish.lite.timing import log_timing_context
from omlish.logs.modules import get_module_logger

from ...env import register_github_env_var
from ..clients import BaseGithubCacheClient
from ..clients import GithubCacheClient
from .api import GithubCacheServiceV2
from .api import GithubCacheServiceV2RequestT
from .api import GithubCacheServiceV2ResponseT
from .azure import AzureBlockBlobUploader


log = get_module_logger(globals())  # noqa


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
            await self._download_file_chunks(
                key=check.non_empty_str(entry2.response.matched_key),
                url=check.non_empty_str(entry2.response.signed_download_url),
                out_file=out_file,
            )

    #

    async def _upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))
        file_size = os.stat(in_file).st_size

        #

        version = str(self._cache_version).zfill(GithubCacheServiceV2.VERSION_LENGTH)

        reserve_resp = check.not_none(await self._send_method_request(
            GithubCacheServiceV2.CREATE_CACHE_ENTRY_METHOD,  # type: ignore[arg-type]
            GithubCacheServiceV2.CreateCacheEntryRequest(
                key=fixed_key,
                version=version,
            ),
        ))
        check.state(reserve_resp.ok)

        log.debug(f'Github cache file {os.path.basename(in_file)} upload reserved for file size {file_size}')  # noqa

        #

        upload_chunks = self._generate_file_upload_chunks(
            in_file=in_file,
            url=reserve_resp.signed_upload_url,
            key=fixed_key,
            file_size=file_size,
        )

        az_chunks = [
            AzureBlockBlobUploader.FileChunk(
                in_file=in_file,
                offset=c.offset,
                size=c.size,
            )
            for c in upload_chunks
        ]

        async def az_make_request(req: AzureBlockBlobUploader.Request) -> AzureBlockBlobUploader.Response:
            u_req = urllib.request.Request(  # noqa
                req.url,
                method=req.method,
                headers=req.headers or {},
                data=req.body,
            )

            u_resp, u_body = await self._send_urllib_request(u_req)

            return AzureBlockBlobUploader.Response(
                status=u_resp.status,
                headers=dict(u_resp.headers),
                data=u_body,
            )

        az_uploader = AzureBlockBlobUploader(
            reserve_resp.signed_upload_url,
            az_make_request,
            concurrency=self._concurrency,
        )

        await az_uploader.upload_file(az_chunks)

        #

        commit_resp = check.not_none(await self._send_method_request(
            GithubCacheServiceV2.FINALIZE_CACHE_ENTRY_METHOD,  # type: ignore[arg-type]
            GithubCacheServiceV2.FinalizeCacheEntryUploadRequest(
                key=fixed_key,
                size_bytes=file_size,
                version=version,
            ),
        ))
        check.state(commit_resp.ok)

        log.debug(f'Github cache file {os.path.basename(in_file)} upload complete, entry id {commit_resp.entry_id}')  # noqa

    async def upload_file(self, key: str, in_file: str) -> None:
        with log_timing_context(
                f'Uploading github cache file {os.path.basename(in_file)} '
                f'key {key}',
        ):
            await self._upload_file(key, in_file)
