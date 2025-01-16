# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import json
import os
import typing as ta

from omlish.lite.check import check
from omlish.lite.contextmanagers import defer
from omlish.subprocesses import subprocesses

from ..cache import ShellCache
from ..shell import ShellCmd
from ..utils import make_temp_file
from .cacheapi import GithubCacheServiceV1


##


class GithubV1CacheShellClient:
    BASE_URL_ENV_KEY = 'ACTIONS_CACHE_URL'
    AUTH_TOKEN_ENV_KEY = 'ACTIONS_RUNTIME_TOKEN'  # noqa

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,
            auth_token: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        if base_url is None:
            base_url = os.environ[self.BASE_URL_ENV_KEY]
        self._base_url = check.non_empty_str(base_url)

        if auth_token is None:
            auth_token = os.environ.get(self.AUTH_TOKEN_ENV_KEY)
        self._auth_token = auth_token

        self._service_url = GithubCacheServiceV1.get_service_url(self._base_url)

    #

    _MISSING = object()

    def build_headers(
            self,
            *,
            auth_token: ta.Any = _MISSING,
            content_type: ta.Optional[str] = None,
    ) -> ta.Dict[str, str]:
        dct = {
            'Accept': f'application/json;{GithubCacheServiceV1.API_VERSION}',
        }

        if auth_token is self._MISSING:
            auth_token = self._auth_token
        if auth_token:
            dct['Authorization'] = f'Bearer {auth_token}'

        if content_type is not None:
            dct['Content-Type'] = content_type

        return dct

    #

    HEADER_AUTH_TOKEN_ENV_KEY = '_GITHUB_CACHE_AUTH_TOKEN'  # noqa

    def build_curl_cmd(
            self,
            method: str,
            url: str,
            *,
            json: bool = False,
            content_type: ta.Optional[str] = None,
    ) -> ShellCmd:
        if content_type is None and json:
            content_type = 'application/json'

        env = {}

        header_auth_token: ta.Optional[str]
        if self._auth_token:
            env[self.HEADER_AUTH_TOKEN_ENV_KEY] = self._auth_token
            header_auth_token = f'${self.HEADER_AUTH_TOKEN_ENV_KEY}'
        else:
            header_auth_token = None

        hdrs = self.build_headers(
            auth_token=header_auth_token,
            content_type=content_type,
        )

        url = f'{self._service_url}/{url}'

        cmd = ' '.join([
            'curl',
            '-s',
            '-X', method,
            url,
            *[f'-H "{k}: {v}"' for k, v in hdrs.items()],
        ])

        return ShellCmd(
            cmd,
            env=env,
        )

    @dc.dataclass()
    class CurlError(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

    @dc.dataclass(frozen=True)
    class CurlResult:
        status_code: int
        body: ta.Optional[bytes]

        def as_error(self) -> 'GithubV1CacheShellClient.CurlError':
            return GithubV1CacheShellClient.CurlError(
                status_code=self.status_code,
                body=self.body,
            )

    def run_curl_cmd(
            self,
            cmd: ShellCmd,
            *,
            raise_: bool = False,
    ) -> CurlResult:
        out_file = make_temp_file()
        with defer(lambda: os.unlink(out_file)):
            run_cmd = dc.replace(cmd, s=f"{cmd.s} -o {out_file} -w '%{{json}}'")

            out_json_bytes = run_cmd.run(subprocesses.check_output)

            out_json = json.loads(out_json_bytes.decode())
            status_code = check.isinstance(out_json['response_code'], int)

            with open(out_file, 'rb') as f:
                body = f.read()

            result = self.CurlResult(
                status_code=status_code,
                body=body,
            )

        if raise_ and (500 <= status_code <= 600):
            raise result.as_error()

        return result

    def run_json_curl_cmd(
            self,
            cmd: ShellCmd,
            *,
            success_status_codes: ta.Optional[ta.Container[int]] = None,
    ) -> ta.Optional[ta.Any]:
        result = self.run_curl_cmd(cmd, raise_=True)

        if success_status_codes is not None:
            is_success = result.status_code in success_status_codes
        else:
            is_success = 200 <= result.status_code < 300

        if is_success:
            if (body := result.body) is None:
                return None
            return json.loads(body.decode('utf-8-sig'))

        elif result.status_code == 404:
            return None

        else:
            raise result.as_error()

    #

    def build_get_entry_curl_cmd(self, key: str) -> ShellCmd:
        return self.build_curl_cmd(
            'GET',
            f'cache?keys={key}',
        )

    def run_get_entry(self, key: str) -> ta.Optional[GithubCacheServiceV1.ArtifactCacheEntry]:
        curl_cmd = self.build_get_entry_curl_cmd(key)

        obj = self.run_json_curl_cmd(
            curl_cmd,
            success_status_codes=[200],
        )
        if obj is None:
            return None

        return GithubCacheServiceV1.load_dataclass(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        )

    #

    def build_download_get_entry_cmd(
            self,
            entry: GithubCacheServiceV1.ArtifactCacheEntry,
            out_file: str,
    ) -> ShellCmd:
        return ShellCmd(' '.join([
            'aria2c',
            '-x', '4',
            '-o', out_file,
            check.non_empty_str(entry.archive_location),
        ]))

    def download_get_entry(
            self,
            entry: GithubCacheServiceV1.ArtifactCacheEntry,
            out_file: str,
    ) -> None:
        dl_cmd = self.build_download_get_entry_cmd(entry, out_file)
        dl_cmd.run(subprocesses.check_call)


##


class GithubShellCache(ShellCache):
    def __init__(
            self,
            local: ShellCache,
            *,
            client: ta.Optional[GithubV1CacheShellClient] = None,
    ) -> None:
        super().__init__()

        self._local = local

        if client is None:
            client = GithubV1CacheShellClient()
        self._client = client

    def get_file_cmd(self, key: str) -> ta.Optional[ShellCmd]:
        if (local_cmd := self._local.get_file_cmd(key)) is not None:
            return local_cmd

        if (entry := self._client.run_get_entry(key)) is None:
            return None

        tmp_file = make_temp_file()
        with defer(lambda: os.unlink(tmp_file)):
            self._client.download_get_entry(entry, tmp_file)

            with self._local.put_file_cmd(key) as put:
                put_cmd = dc.replace(put.cmd, s=f'cat {tmp_file} | {put.cmd.s}')
                put_cmd.run(subprocesses.check_call)

        return check.not_none(self._local.get_file_cmd(key))

    def put_file_cmd(self, key: str) -> ShellCache.PutFileCmdContext:
        raise NotImplementedError
