# ruff: noqa: TC003 UP006 UP007
import abc
import dataclasses as dc
import os
import typing as ta
import urllib.parse
import urllib.request

from omlish.asyncs.asyncio.utils import asyncio_wait_concurrent
from omlish.lite.check import check
from omlish.lite.logs import log
from omlish.lite.timing import log_timing_context

from ...env import register_github_env_var
from ..clients import BaseGithubCacheClient
from ..clients import GithubCacheClient
from .api import GithubCacheServiceV1


##


class BaseV1GithubCacheClient(BaseGithubCacheClient, abc.ABC):
    BASE_URL_ENV_VAR = register_github_env_var('ACTIONS_CACHE_URL')

    #

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

    def build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, str]:
        return super().build_request_headers(
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

    def build_get_entry_url_path(self, *keys: str) -> str:
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


class GithubCacheServiceV1Client(BaseV1GithubCacheClient):
    DEFAULT_CONCURRENCY = 4

    DEFAULT_CHUNK_SIZE = 32 * 1024 * 1024

    def __init__(
            self,
            *,
            concurrency: int = DEFAULT_CONCURRENCY,
            chunk_size: int = DEFAULT_CHUNK_SIZE,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        check.arg(concurrency > 0)
        self._concurrency = concurrency

        check.arg(chunk_size > 0)
        self._chunk_size = chunk_size

    #

    async def get_entry(self, key: str) -> ta.Optional[GithubCacheClient.Entry]:
        obj = await self.send_service_request(
            self.build_get_entry_url_path(self.fix_key(key, partial_suffix=True)),
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    #

    @dc.dataclass(frozen=True)
    class _DownloadChunk:
        key: str
        url: str
        out_file: str
        offset: int
        size: int

    async def _download_file_chunk_urllib(self, chunk: _DownloadChunk) -> None:
        req = urllib.request.Request(  # noqa
            chunk.url,
            headers={
                'Range': f'bytes={chunk.offset}-{chunk.offset + chunk.size - 1}',
            },
        )

        _, buf_ = await self.send_url_request(req)

        buf = check.not_none(buf_)
        check.equal(len(buf), chunk.size)

        #

        def write_sync():
            with open(chunk.out_file, 'r+b') as f:  # noqa
                f.seek(chunk.offset, os.SEEK_SET)
                f.write(buf)

        await self._get_loop().run_in_executor(None, write_sync)  # noqa

    # async def _download_file_chunk_curl(self, chunk: _DownloadChunk) -> None:
    #     async with contextlib.AsyncExitStack() as es:
    #         f = open(chunk.out_file, 'r+b')
    #         f.seek(chunk.offset, os.SEEK_SET)
    #
    #         tmp_file = es.enter_context(temp_file_context())  # noqa
    #
    #         proc = await es.enter_async_context(asyncio_subprocesses.popen(
    #             'curl',
    #             '-s',
    #             '-w', '%{json}',
    #             '-H', f'Range: bytes={chunk.offset}-{chunk.offset + chunk.size - 1}',
    #             chunk.url,
    #             output=subprocess.PIPE,
    #         ))
    #
    #         futs = asyncio.gather(
    #
    #         )
    #
    #         await proc.wait()
    #
    #         with open(tmp_file, 'r') as f:  # noqa
    #             curl_json = tmp_file.read()
    #
    #     curl_res = json.loads(curl_json.decode().strip())
    #
    #     status_code = check.isinstance(curl_res['response_code'], int)
    #
    #     if not (200 <= status_code <= 300):
    #         raise RuntimeError(f'Curl chunk download {chunk} failed: {curl_res}')

    async def _download_file_chunk(self, chunk: _DownloadChunk) -> None:
        with log_timing_context(
                'Downloading github cache '
                f'key {chunk.key} '
                f'file {chunk.out_file} '
                f'chunk {chunk.offset} - {chunk.offset + chunk.size}',
        ):
            await self._download_file_chunk_urllib(chunk)

    async def _download_file(self, entry: BaseV1GithubCacheClient.Entry, out_file: str) -> None:
        key = check.non_empty_str(entry.artifact.cache_key)
        url = check.non_empty_str(entry.artifact.archive_location)

        head_resp, _ = await self.send_url_request(urllib.request.Request(  # noqa
            url,
            method='HEAD',
        ))
        file_size = int(head_resp.headers['Content-Length'])

        #

        with open(out_file, 'xb') as f:  # noqa
            f.truncate(file_size)

        #

        download_tasks = []
        chunk_size = self._chunk_size
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            offset = i * chunk_size
            size = min(chunk_size, file_size - offset)
            chunk = self._DownloadChunk(
                key,
                url,
                out_file,
                offset,
                size,
            )
            download_tasks.append(self._download_file_chunk(chunk))

        await asyncio_wait_concurrent(download_tasks, self._concurrency)

    async def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        entry1 = check.isinstance(entry, self.Entry)
        with log_timing_context(
                'Downloading github cache '
                f'key {entry1.artifact.cache_key} '
                f'version {entry1.artifact.cache_version} '
                f'to {out_file}',
        ):
            await self._download_file(entry1, out_file)

    #

    async def _upload_file_chunk(
            self,
            key: str,
            cache_id: int,
            in_file: str,
            offset: int,
            size: int,
    ) -> None:
        with log_timing_context(
                f'Uploading github cache {key} '
                f'file {in_file} '
                f'chunk {offset} - {offset + size}',
        ):
            with open(in_file, 'rb') as f:  # noqa
                f.seek(offset)
                buf = f.read(size)

            check.equal(len(buf), size)

            await self.send_service_request(
                f'caches/{cache_id}',
                method='PATCH',
                content_type='application/octet-stream',
                headers={
                    'Content-Range': f'bytes {offset}-{offset + size - 1}/*',
                },
                content=buf,
                success_status_codes=[204],
            )

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
        reserve_resp_obj = await self.send_service_request(
            'caches',
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

        upload_tasks = []
        chunk_size = self._chunk_size
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            offset = i * chunk_size
            size = min(chunk_size, file_size - offset)
            upload_tasks.append(self._upload_file_chunk(
                fixed_key,
                cache_id,
                in_file,
                offset,
                size,
            ))

        await asyncio_wait_concurrent(upload_tasks, self._concurrency)

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        await self.send_service_request(
            f'caches/{cache_id}',
            json_content=GithubCacheServiceV1.dataclass_to_json(commit_req),
            success_status_codes=[204],
        )

    async def upload_file(self, key: str, in_file: str) -> None:
        with log_timing_context(
                f'Uploading github cache file {os.path.basename(in_file)} '
                f'key {key}',
        ):
            await self._upload_file(key, in_file)
