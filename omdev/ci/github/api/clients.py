# ruff: noqa: UP006 UP007 UP045
import abc
import asyncio
import dataclasses as dc
import http.client
import itertools
import json
import os
import typing as ta
import urllib.parse
import urllib.request

from omlish.asyncs.asyncio.utils import asyncio_wait_concurrent
from omlish.http.urllib import NonRaisingUrllibErrorProcessor
from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.json import json_dumps_compact
from omlish.lite.timing import log_timing_context
from omlish.logs.modules import get_module_logger

from ...consts import CI_CACHE_VERSION
from ..env import register_github_env_var


log = get_module_logger(globals())  # noqa


##


class GithubCacheClient(Abstract):
    @dc.dataclass(frozen=True)
    class Entry(Abstract):
        pass

    @abc.abstractmethod
    def get_entry(self, key: str) -> ta.Awaitable[ta.Optional[Entry]]:
        raise NotImplementedError

    def get_entry_url(self, entry: Entry) -> ta.Optional[str]:
        return None

    @abc.abstractmethod
    def download_file(self, entry: Entry, out_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, key: str, in_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class BaseGithubCacheClient(GithubCacheClient, Abstract):
    AUTH_TOKEN_ENV_VAR = register_github_env_var('ACTIONS_RUNTIME_TOKEN')  # noqa

    KEY_SUFFIX_ENV_VAR = register_github_env_var('GITHUB_RUN_ID')

    DEFAULT_CONCURRENCY = 4
    DEFAULT_CHUNK_SIZE = 64 * 1024 * 1024

    #

    def __init__(
            self,
            *,
            service_url: str,

            auth_token: ta.Optional[str] = None,

            key_prefix: ta.Optional[str] = None,
            key_suffix: ta.Optional[str] = None,

            cache_version: int = CI_CACHE_VERSION,

            loop: ta.Optional[asyncio.AbstractEventLoop] = None,

            concurrency: int = DEFAULT_CONCURRENCY,
            chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        super().__init__()

        #

        self._service_url = check.non_empty_str(service_url)

        if auth_token is None:
            auth_token = self.AUTH_TOKEN_ENV_VAR()
        self._auth_token = auth_token

        #

        self._key_prefix = key_prefix

        if key_suffix is None:
            key_suffix = self.KEY_SUFFIX_ENV_VAR()
        self._key_suffix = check.non_empty_str(key_suffix)

        #

        self._cache_version = check.isinstance(cache_version, int)

        #

        self._given_loop = loop

        #

        check.arg(concurrency > 0)
        self._concurrency = concurrency

        check.arg(chunk_size > 0)
        self._chunk_size = chunk_size

    ##
    # misc

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if (loop := self._given_loop) is not None:
            return loop
        return asyncio.get_running_loop()

    #

    def _load_json_bytes(self, b: ta.Optional[bytes]) -> ta.Optional[ta.Any]:
        if not b:
            return None
        return json.loads(b.decode('utf-8-sig'))

    ##
    # requests

    def _build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            *,
            no_auth: bool = False,
            content_type: ta.Optional[str] = None,
            json_content: bool = False,
    ) -> ta.Dict[str, str]:
        dct = {}

        if not no_auth and (auth_token := self._auth_token):
            dct['Authorization'] = f'Bearer {auth_token}'

        if content_type is None and json_content:
            content_type = 'application/json'
        if content_type is not None:
            dct['Content-Type'] = content_type

        if headers:
            dct.update(headers)

        return dct

    #

    async def _send_urllib_request(
            self,
            req: urllib.request.Request,
    ) -> ta.Tuple[http.client.HTTPResponse, ta.Optional[bytes]]:
        def run_sync():
            opener = urllib.request.build_opener(NonRaisingUrllibErrorProcessor)
            with opener.open(req) as resp:  # noqa
                body = resp.read()
            return (resp, body)

        return await self._get_loop().run_in_executor(None, run_sync)  # noqa

    #

    @dc.dataclass()
    class ServiceRequestError(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

        def __str__(self) -> str:
            return repr(self)

    async def _send_request(
            self,
            *,
            url: ta.Optional[str] = None,
            path: ta.Optional[str] = None,

            method: ta.Optional[str] = None,

            headers: ta.Optional[ta.Mapping[str, str]] = None,
            no_auth: bool = False,
            content_type: ta.Optional[str] = None,

            content: ta.Optional[bytes] = None,
            json_content: ta.Optional[ta.Any] = None,

            success_status_codes: ta.Optional[ta.Container[int]] = None,

            retry_status_codes: ta.Optional[ta.Container[int]] = None,
            num_retries: int = 0,
            retry_sleep: ta.Optional[float] = None,
    ) -> ta.Optional[ta.Any]:
        if url is not None and path is not None:
            raise RuntimeError('Must not pass both url and path')
        elif path is not None:
            url = f'{self._service_url}/{path}'
        url = check.non_empty_str(url)

        if content is not None and json_content is not None:
            raise RuntimeError('Must not pass both content and json_content')
        elif json_content is not None:
            content = json_dumps_compact(json_content).encode('utf-8')
            header_json_content = True
        else:
            header_json_content = False

        if method is None:
            method = 'POST' if content is not None else 'GET'

        headers = self._build_request_headers(
            headers,
            no_auth=no_auth,
            content_type=content_type,
            json_content=header_json_content,
        )

        #

        for n in itertools.count():
            req = urllib.request.Request(  # noqa
                url,
                method=method,
                headers=headers,
                data=content,
            )

            resp, body = await self._send_urllib_request(req)

            #

            if success_status_codes is not None:
                is_success = resp.status in success_status_codes
            else:
                is_success = (200 <= resp.status < 300)
            if is_success:
                return self._load_json_bytes(body)

            #

            log.debug(f'Request to url {url} got unsuccessful status code {resp.status}')  # noqa

            if not (
                retry_status_codes is not None and
                resp.status in retry_status_codes and
                n < num_retries
            ):
                raise self.ServiceRequestError(resp.status, body)

            if retry_sleep is not None:
                await asyncio.sleep(retry_sleep)

        raise RuntimeError('Unreachable')

    ##
    # keys

    KEY_PART_SEPARATOR = '---'

    def fix_key(self, s: str, partial_suffix: bool = False) -> str:
        return self.KEY_PART_SEPARATOR.join([
            *([self._key_prefix] if self._key_prefix else []),
            s,
            ('' if partial_suffix else self._key_suffix),
        ])

    ##
    # downloading

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

        _, buf_ = await self._send_urllib_request(req)

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
    #     if not (200 <= status_code < 300):
    #         raise RuntimeError(f'Curl chunk download {chunk} failed: {curl_res}')

    async def _download_file_chunk(self, chunk: _DownloadChunk) -> None:
        with log_timing_context(
                'Downloading github cache '
                f'key {chunk.key} '
                f'file {chunk.out_file} '
                f'chunk {chunk.offset} - {chunk.offset + chunk.size}',
        ):
            await self._download_file_chunk_urllib(chunk)

    async def _download_file_chunks(
            self,
            *,
            key: str,
            url: str,
            out_file: str,
    ) -> None:
        check.non_empty_str(key)
        check.non_empty_str(url)

        head_resp, _ = await self._send_urllib_request(urllib.request.Request(  # noqa
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

    ##
    # uploading

    @dc.dataclass(frozen=True)
    class _UploadChunk:
        url: str
        key: str
        in_file: str
        offset: int
        size: int

    UPLOAD_CHUNK_NUM_RETRIES = 10
    UPLOAD_CHUNK_RETRY_SLEEP = .5

    async def _upload_file_chunk_(self, chunk: _UploadChunk) -> None:
        with open(chunk.in_file, 'rb') as f:  # noqa
            f.seek(chunk.offset)
            buf = f.read(chunk.size)

        check.equal(len(buf), chunk.size)

        await self._send_request(
            url=chunk.url,

            method='PATCH',

            headers={
                'Content-Range': f'bytes {chunk.offset}-{chunk.offset + chunk.size - 1}/*',
            },
            no_auth=True,
            content_type='application/octet-stream',

            content=buf,

            success_status_codes=[204],

            # retry_status_codes=[405],
            num_retries=self.UPLOAD_CHUNK_NUM_RETRIES,
            retry_sleep=self.UPLOAD_CHUNK_RETRY_SLEEP,
        )

    async def _upload_file_chunk(self, chunk: _UploadChunk) -> None:
        with log_timing_context(
                f'Uploading github cache {chunk.key} '
                f'file {chunk.in_file} '
                f'chunk {chunk.offset} - {chunk.offset + chunk.size}',
        ):
            await self._upload_file_chunk_(chunk)

    def _generate_file_upload_chunks(
            self,
            *,
            in_file: str,
            url: str,
            key: str,

            file_size: ta.Optional[int] = None,
    ) -> ta.List[_UploadChunk]:
        check.state(os.path.isfile(in_file))

        if file_size is None:
            file_size = os.stat(in_file).st_size

        #

        upload_chunks: ta.List[BaseGithubCacheClient._UploadChunk] = []
        chunk_size = self._chunk_size
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            offset = i * chunk_size
            size = min(chunk_size, file_size - offset)
            upload_chunks.append(self._UploadChunk(
                url=url,
                key=key,
                in_file=in_file,
                offset=offset,
                size=size,
            ))

        return upload_chunks

    async def _upload_file_chunks(
            self,
            *,
            in_file: str,
            url: str,
            key: str,

            file_size: ta.Optional[int] = None,
    ) -> None:
        upload_tasks = []
        for chunk in self._generate_file_upload_chunks(
            in_file=in_file,
            url=url,
            key=key,
            file_size=file_size,
        ):
            upload_tasks.append(self._upload_file_chunk(chunk))

        await asyncio_wait_concurrent(upload_tasks, self._concurrency)
