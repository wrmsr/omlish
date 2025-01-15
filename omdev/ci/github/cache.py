# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import json
import os
import typing as ta

from omlish.lite.check import check
from omlish.lite.contextmanagers import defer
from omlish.subprocesses import subprocesses

from ..cache import FileCache
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

    AUTH_TOKEN_ENV_KEY = '_GITHUB_CACHE_AUTH_TOKEN'  # noqa

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
            env[self.AUTH_TOKEN_ENV_KEY] = self._auth_token
            header_auth_token = f'${self.AUTH_TOKEN_ENV_KEY}'
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

    @dc.dataclass(frozen=True)
    class CurlResult:
        status_code: int
        body: ta.Optional[bytes]

    def run_curl_cmd(self, cmd: ShellCmd) -> CurlResult:
        out_file = make_temp_file()
        with defer(lambda: os.unlink(out_file)):
            run_cmd = dc.replace(cmd, s=f"{cmd.s} -o {out_file} -w '%{{json}}'")

            out_json_bytes = run_cmd.run(subprocesses.check_output)

            out_json = json.loads(out_json_bytes.decode())
            status_code = check.isinstance(out_json['response_code'], int)

            with open(out_file, 'rb') as f:
                body = f.read()

            return self.CurlResult(
                status_code=status_code,
                body=body,
            )

    #

    def build_get_curl_cmd(self, key: str) -> ShellCmd:
        return self.build_curl_cmd(
            'GET',
            f'cache?keys={key}',
        )

    def run_get(self, key: str) -> ta.Any:
        get_curl_cmd = self.build_get_curl_cmd(key)
        result = self.run_curl_cmd(get_curl_cmd)
        return result


##


class GithubV1FileCache(FileCache):
    def __init__(self, client: GithubV1CacheShellClient) -> None:
        super().__init__()

        self._client = client

    def get_file(self, key: str) -> ta.Optional[str]:
        raise NotImplementedError

    def put_file(self, key: str, file_path: str) -> ta.Optional[str]:
        raise NotImplementedError
