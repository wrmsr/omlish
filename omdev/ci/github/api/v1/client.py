# ruff: noqa: TC003 UP006 UP007 UP045
import dataclasses as dc
import os
import typing as ta
import urllib.parse
import urllib.request

from omlish.lite.check import check
from omlish.lite.timing import log_timing_context
from omlish.logs.modules import get_module_logger

from ...env import register_github_env_var
from ..clients import BaseGithubCacheClient
from ..clients import GithubCacheClient
from .api import GithubCacheServiceV1


log = get_module_logger(globals())  # noqa


##


class GithubCacheServiceV1Client(BaseGithubCacheClient):
    BASE_URL_ENV_VAR = register_github_env_var('ACTIONS_CACHE_URL')

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> None:
        if base_url is None:
            base_url = check.non_empty_str(self.BASE_URL_ENV_VAR())
        service_url = GithubCacheServiceV1.get_service_url(base_url)

        super().__init__(
            service_url=service_url,
            **kwargs,
        )

    #

    def _build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, str]:
        return super()._build_request_headers(
            {
                'Accept': ';'.join([
                    'application/json',
                    f'api-version={GithubCacheServiceV1.API_VERSION}',
                ]),
                **(headers or {}),
            },
            **kwargs,
        )

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        artifact: GithubCacheServiceV1.ArtifactCacheEntry

    def get_entry_url(self, entry: GithubCacheClient.Entry) -> ta.Optional[str]:
        entry1 = check.isinstance(entry, self.Entry)
        return entry1.artifact.archive_location

    #

    def _build_get_entry_url_path(self, *keys: str) -> str:
        qp = dict(
            keys=','.join(urllib.parse.quote_plus(k) for k in keys),
            version=str(self._cache_version),
        )

        return '?'.join([
            'cache',
            '&'.join([
                f'{k}={v}'
                for k, v in qp.items()
            ]),
        ])

    GET_ENTRY_SUCCESS_STATUS_CODES = (200, 204)

    #

    async def get_entry(self, key: str) -> ta.Optional[GithubCacheClient.Entry]:
        obj = await self._send_request(
            path=self._build_get_entry_url_path(self.fix_key(key, partial_suffix=True)),
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    #

    async def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        entry1 = check.isinstance(entry, self.Entry)
        with log_timing_context(
                'Downloading github cache '
                f'key {entry1.artifact.cache_key} '
                f'version {entry1.artifact.cache_version} '
                f'to {out_file}',
        ):
            await self._download_file_chunks(
                key=check.non_empty_str(entry1.artifact.cache_key),
                url=check.non_empty_str(entry1.artifact.archive_location),
                out_file=out_file,
            )

    #

    async def _upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))
        file_size = os.stat(in_file).st_size

        #

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=fixed_key,
            cache_size=file_size,
            version=str(self._cache_version),
        )
        reserve_resp_obj = await self._send_request(
            path='caches',
            json_content=GithubCacheServiceV1.dataclass_to_json(reserve_req),
            success_status_codes=[201],
        )
        reserve_resp = GithubCacheServiceV1.dataclass_from_json(  # noqa
            GithubCacheServiceV1.ReserveCacheResponse,
            reserve_resp_obj,
        )
        cache_id = check.isinstance(reserve_resp.cache_id, int)

        log.debug(f'Github cache file {os.path.basename(in_file)} got id {cache_id}')  # noqa

        #

        url = f'{self._service_url}/caches/{cache_id}'

        await self._upload_file_chunks(
            in_file=in_file,
            url=url,
            key=fixed_key,
            file_size=file_size,
        )

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        await self._send_request(
            path=f'caches/{cache_id}',
            json_content=GithubCacheServiceV1.dataclass_to_json(commit_req),
            success_status_codes=[204],
        )

    async def upload_file(self, key: str, in_file: str) -> None:
        with log_timing_context(
                f'Uploading github cache file {os.path.basename(in_file)} '
                f'key {key}',
        ):
            await self._upload_file(key, in_file)
