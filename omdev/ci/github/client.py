# ruff: noqa: TC003 UP006 UP007
# @omlish-lite
import abc
import dataclasses as dc
import http.client
import json
import os
import shlex
import typing as ta
import urllib.parse
import urllib.request

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.lite.json import json_dumps_compact

from ..shell import ShellCmd
from .api import GithubCacheServiceV1


##


class GithubCacheClient(abc.ABC):
    class Entry(abc.ABC):  # noqa
        pass

    @abc.abstractmethod
    def get_entry(self, key: str) -> ta.Awaitable[ta.Optional[Entry]]:
        raise NotImplementedError

    @abc.abstractmethod
    def download_file(self, entry: Entry, out_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, key: str, in_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class GithubCacheServiceV1BaseClient(GithubCacheClient, abc.ABC):
    BASE_URL_ENV_KEY = 'ACTIONS_CACHE_URL'
    AUTH_TOKEN_ENV_KEY = 'ACTIONS_RUNTIME_TOKEN'  # noqa

    KEY_SUFFIX_ENV_KEY = 'GITHUB_RUN_ID'

    CACHE_VERSION: ta.ClassVar[int] = 1

    #

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,
            auth_token: ta.Optional[str] = None,

            key_prefix: ta.Optional[str] = None,
            key_suffix: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        #

        if base_url is None:
            base_url = os.environ[self.BASE_URL_ENV_KEY]
        self._service_url = GithubCacheServiceV1.get_service_url(base_url)

        if auth_token is None:
            auth_token = os.environ.get(self.AUTH_TOKEN_ENV_KEY)
        self._auth_token = auth_token

        #

        self._key_prefix = key_prefix

        if key_suffix is None:
            key_suffix = os.environ[self.KEY_SUFFIX_ENV_KEY]
        self._key_suffix = check.non_empty_str(key_suffix)

    #

    def build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            *,
            content_type: ta.Optional[str] = None,
            json_content: bool = False,
    ) -> ta.Dict[str, str]:
        dct = {
            'Accept': ';'.join([
                'application/json',
                f'api-version={GithubCacheServiceV1.API_VERSION}',
            ]),
        }

        if (auth_token := self._auth_token):
            dct['Authorization'] = f'Bearer {auth_token}'

        if content_type is None and json_content:
            content_type = 'application/json'
        if content_type is not None:
            dct['Content-Type'] = content_type

        if headers:
            dct.update(headers)

        return dct

    #

    def load_json_bytes(self, b: ta.Optional[bytes]) -> ta.Optional[ta.Any]:
        if not b:
            return None
        return json.loads(b.decode('utf-8-sig'))

    #

    @dc.dataclass()
    class RequestError(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

        def __str__(self) -> str:
            return repr(self)

    async def send_request(
            self,
            path: str,
            *,
            method: ta.Optional[str] = None,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            content_type: ta.Optional[str] = None,
            content: ta.Optional[bytes] = None,
            json_content: ta.Optional[ta.Any] = None,
            success_status_codes: ta.Optional[ta.Container[int]] = None,
    ) -> ta.Optional[ta.Any]:
        url = f'{self._service_url}/{path}'

        if content is not None and json_content is not None:
            raise RuntimeError('Must not pass both content and json_content')
        elif json_content is not None:
            content = json_dumps_compact(json_content).encode('utf-8')
            header_json_content = True
        else:
            header_json_content = False

        if method is None:
            method = 'POST' if content is not None else 'GET'

        resp: http.client.HTTPResponse
        with urllib.request.urlopen(urllib.request.Request(  # noqa
                url,
                method=method,
                headers=self.build_request_headers(
                    headers,
                    content_type=content_type,
                    json_content=header_json_content,
                ),
                data=content,
        )) as resp:
            body = resp.read()

        if success_status_codes is not None:
            is_success = resp.status in success_status_codes
        else:
            is_success = (200 <= resp.status <= 300)
        if not is_success:
            raise self.RequestError(resp.status, body)

        return self.load_json_bytes(body)

    #

    KEY_PART_SEPARATOR = '--'

    def fix_key(self, s: str, partial_suffix: bool = False) -> str:
        return self.KEY_PART_SEPARATOR.join([
            *([self._key_prefix] if self._key_prefix else []),
            s,
            ('' if partial_suffix else self._key_suffix),
        ])

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        artifact: GithubCacheServiceV1.ArtifactCacheEntry

    #

    def build_get_entry_url_path(self, *keys: str) -> str:
        qp = dict(
            keys=','.join(urllib.parse.quote_plus(k) for k in keys),
            version=str(self.CACHE_VERSION),
        )

        return '?'.join([
            'cache',
            '&'.join([
                f'{k}={v}'
                for k, v in qp.items()
            ]),
        ])

    GET_ENTRY_SUCCESS_STATUS_CODES = (200, 204)


##


class GithubCacheServiceV1Client(GithubCacheServiceV1BaseClient):
    async def get_entry(self, key: str) -> ta.Optional[GithubCacheServiceV1BaseClient.Entry]:
        obj = await self.send_request(
            self.build_get_entry_url_path(self.fix_key(key, partial_suffix=True)),
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    #

    async def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        dl_url = check.non_empty_str(check.isinstance(entry, self.Entry).artifact.archive_location)

        dl_cmd = ShellCmd(' '.join([
            'aria2c',
            '-x', '4',
            '-o', out_file,
            shlex.quote(dl_url),
        ]))

        await dl_cmd.run(asyncio_subprocesses.check_call)

    #

    async def _upload_file_chunk(
            self,
            cache_id: int,
            in_file: str,
            offset: int,
            size: int,
    ) -> None:
        with open(in_file, 'rb') as f:  # noqa
            f.seek(offset)
            buf = f.read(size)

        check.equal(len(buf), size)

        await self.send_request(
            f'caches/{cache_id}',
            method='PATCH',
            content_type='application/octet-stream',
            headers={
                'Content-Range': f'bytes {offset}-{offset + size - 1}/*',
            },
            content=buf,
            success_status_codes=[204],
        )

    async def upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))

        file_size = os.stat(in_file).st_size

        #

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=fixed_key,
            cache_size=file_size,
            version=str(self.CACHE_VERSION),
        )
        reserve_resp_obj = await self.send_request(
            'caches',
            json_content=GithubCacheServiceV1.dataclass_to_json(reserve_req),
            success_status_codes=[201],
        )
        reserve_resp = GithubCacheServiceV1.dataclass_from_json(  # noqa
            GithubCacheServiceV1.ReserveCacheResponse,
            reserve_resp_obj,
        )
        cache_id = check.isinstance(reserve_resp.cache_id, int)

        #

        chunk_size = 32 * 1024 * 1024
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            offset = i * chunk_size
            size = min(chunk_size, file_size - offset)

            await self._upload_file_chunk(
                cache_id,
                in_file,
                offset,
                size,
            )

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        await self.send_request(
            f'caches/{cache_id}',
            json_content=GithubCacheServiceV1.dataclass_to_json(commit_req),
            success_status_codes=[204],
        )
