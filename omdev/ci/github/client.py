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

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.json import json_dumps_compact
from omlish.subprocesses import subprocesses

from ..shell import ShellCmd
from ..utils import make_temp_file
from .api import GithubCacheServiceV1
from .curl import GithubServiceCurlClient


##


class GithubCacheClient(abc.ABC):
    class Entry(abc.ABC):  # noqa
        pass

    @abc.abstractmethod
    def get_entry(self, key: str) -> ta.Optional[Entry]:
        raise NotImplementedError

    @abc.abstractmethod
    def download_file(self, entry: Entry, out_file: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, key: str, in_file: str) -> None:
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


class GithubCacheServiceV1UrllibClient(GithubCacheServiceV1BaseClient):
    @dc.dataclass()
    class RequestError(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

        def __str__(self) -> str:
            return repr(self)

    def send_request(
            self,
            path: str,
            *,
            method: ta.Optional[str] = None,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            content_type: ta.Optional[str] = None,
            content: ta.Optional[bytes] = None,
            json_content: ta.Optional[ta.Any] = None,
            success_status_codes: ta.Optional[ta.Container[int]] = (200,),
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
            check.in_(resp.status, self.GET_ENTRY_SUCCESS_STATUS_CODES)
            body = resp.read()

        if success_status_codes is not None:
            is_success = resp.status not in success_status_codes
        else:
            is_success = (200 <= resp.status <= 300)
        if not is_success:
            raise self.RequestError(resp.status, body)

        return self.load_json_bytes(body)

    #

    def get_entry(self, key: str) -> ta.Optional[GithubCacheServiceV1BaseClient.Entry]:
        url = f'{self._service_url}/{self.build_get_entry_url_path(self.fix_key(key, partial_suffix=True))}'

        obj = self.send_request(
            url,
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        dl_url = check.non_empty_str(check.isinstance(entry, self.Entry).artifact.archive_location)

        dl_cmd = ShellCmd(' '.join([
            'aria2c',
            '-x', '4',
            '-o', out_file,
            shlex.quote(dl_url),
        ]))

        dl_cmd.run(subprocesses.check_call)

    def upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))

        file_size = os.stat(in_file).st_size

        #

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=fixed_key,
            cache_size=file_size,
            version=str(self.CACHE_VERSION),
        )
        reserve_resp_obj = self.send_request(
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

        print(f'{file_size=}')
        num_written = 0
        chunk_size = 32 * 1024 * 1024
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            ofs = i * chunk_size
            sz = min(chunk_size, file_size - ofs)

            with open(in_file, 'rb') as f:
                f.seek(ofs)
                buf = f.read(sz)

            self.send_request(
                f'caches/{cache_id}',
                method='PATCH',
                content_type='application/octet-stream',
                headers={
                    'Content-Range': f'bytes {ofs}-{ofs + sz - 1}/*',
                },
                content=buf,
                success_status_codes=[204],
            )

            num_written += len(buf)
            print(f'{num_written=}')

            ofs += sz

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        self.send_request(
            f'caches/{cache_id}',
            json_content=GithubCacheServiceV1.dataclass_to_json(commit_req),
            success_status_codes=[204],
        )


##


class GithubCacheServiceV1CurlClient(GithubCacheServiceV1BaseClient):
    @cached_nullary
    def _curl(self) -> GithubServiceCurlClient:
        return GithubServiceCurlClient(
            self._service_url,
            self._auth_token,
            api_version=GithubCacheServiceV1.API_VERSION,
        )

    #

    def build_get_entry_curl_cmd(self, key: str) -> ShellCmd:
        return self._curl().build_cmd(
            'GET',
            shlex.quote(self.build_get_entry_url_path(self.fix_key(key, partial_suffix=True))),
        )

    def get_entry(self, key: str) -> ta.Optional[GithubCacheServiceV1BaseClient.Entry]:
        curl_cmd = self.build_get_entry_curl_cmd(key)

        obj = self._curl().run_json_cmd(
            curl_cmd,
            success_status_codes=self.GET_ENTRY_SUCCESS_STATUS_CODES,
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    #

    def build_download_get_entry_cmd(self, entry: GithubCacheServiceV1BaseClient.Entry, out_file: str) -> ShellCmd:
        return ShellCmd(' '.join([
            'aria2c',
            '-x', '4',
            '-o', out_file,
            shlex.quote(check.non_empty_str(entry.artifact.archive_location)),
        ]))

    def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        dl_cmd = self.build_download_get_entry_cmd(
            check.isinstance(entry, self.Entry),
            out_file,
        )
        dl_cmd.run(subprocesses.check_call)

    #

    def upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))

        file_size = os.stat(in_file).st_size

        #

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=fixed_key,
            cache_size=file_size,
            version=str(self.CACHE_VERSION),
        )
        reserve_cmd = self._curl().build_post_json_cmd(
            'caches',
            GithubCacheServiceV1.dataclass_to_json(reserve_req),
        )
        reserve_resp_obj: ta.Any = check.not_none(self._curl().run_json_cmd(
            reserve_cmd,
            success_status_codes=[201],
        ))
        reserve_resp = GithubCacheServiceV1.dataclass_from_json(  # noqa
            GithubCacheServiceV1.ReserveCacheResponse,
            reserve_resp_obj,
        )
        cache_id = check.isinstance(reserve_resp.cache_id, int)

        #

        tmp_file = make_temp_file()

        print(f'{file_size=}')
        num_written = 0
        chunk_size = 32 * 1024 * 1024
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            ofs = i * chunk_size
            sz = min(chunk_size, file_size - ofs)

            patch_cmd = self._curl().build_cmd(
                'PATCH',
                f'caches/{cache_id}',
                content_type='application/octet-stream',
                headers={
                    'Content-Range': f'bytes {ofs}-{ofs + sz - 1}/*',
                },
            )

            #

            # patch_data_cmd = dc.replace(patch_cmd, s=' | '.join([
            #     f'dd if={in_file} bs={chunk_size} skip={i} count=1 status=none',
            #     f'{patch_cmd.s} --data-binary -',
            # ]))
            # print(f'{patch_data_cmd.s=}')
            # patch_result = self._curl().run_cmd(patch_data_cmd, raise_=True)

            #

            with open(in_file, 'rb') as f:
                f.seek(ofs)
                buf = f.read(sz)
            with open(tmp_file, 'wb') as f:
                f.write(buf)
            num_written += len(buf)
            print(f'{num_written=}')
            patch_data_cmd = dc.replace(patch_cmd, s=f'{patch_cmd.s} --data-binary @{tmp_file}')
            print(f'{patch_data_cmd.s=}')
            patch_result = self._curl().run_cmd(patch_data_cmd, raise_=True)

            #

            check.equal(patch_result.status_code, 204)
            ofs += sz

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        commit_cmd = self._curl().build_post_json_cmd(
            f'caches/{cache_id}',
            GithubCacheServiceV1.dataclass_to_json(commit_req),
        )
        commit_result = self._curl().run_cmd(commit_cmd, raise_=True)
        check.equal(commit_result.status_code, 204)
