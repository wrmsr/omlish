# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import json
import os
import shlex
import typing as ta

from omlish.lite.check import check
from omlish.lite.contextmanagers import defer
from omlish.lite.json import json_dumps_compact
from omlish.subprocesses import subprocesses

from ..cache import DirectoryFileCache
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
            'Accept': f'application/json;api-version={GithubCacheServiceV1.API_VERSION}',
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
            json_content: bool = False,
            content_type: ta.Optional[str] = None,
    ) -> ShellCmd:
        if content_type is None and json_content:
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

    def build_post_json_curl_cmd(
            self,
            url: str,
            obj: ta.Any,
            **kwargs: ta.Any,
    ) -> ShellCmd:
        curl_cmd = self.build_curl_cmd(
            'POST',
            url,
            json_content=True,
            **kwargs,
        )

        obj_json = json_dumps_compact(obj)

        return dc.replace(curl_cmd, s=f'echo {shlex.quote(obj_json)} | {curl_cmd.s} -d -')

    #

    @dc.dataclass()
    class CurlError(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

        def __str__(self) -> str:
            return repr(self)

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
            if not (body := result.body):
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
            success_status_codes=[200, 204],
        )
        if obj is None:
            return None

        return GithubCacheServiceV1.dataclass_from_json(
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

    #

    def upload_cache_entry(
            self,
            key: str,
            in_file: str,
    ) -> None:
        """
        export CACHE_ID=$(curl \
          -v \
          -X POST \
          "${ACTIONS_CACHE_URL}_apis/artifactcache/caches" \
          -H 'Content-Type: application/json' \
          -H 'Accept: application/json;api-version=6.0-preview.1' \
          -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
          -d '{"key": "'"$CACHE_KEY"'", "cacheSize": '"$FILE_SIZE"'}' \
          | jq .cacheId)

        curl \
          -v \
          -X PATCH \
          "${ACTIONS_CACHE_URL}_apis/artifactcache/caches/$CACHE_ID" \
          -H 'Content-Type: application/octet-stream' \
          -H 'Accept: application/json;api-version=6.0-preview.1' \
          -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
          -H "Content-Range: bytes 0-$((FILE_SIZE - 1))/*" \
          --data-binary @"$FILE"

        curl \
          -v \
          -X POST \
          "${ACTIONS_CACHE_URL}_apis/artifactcache/caches/$CACHE_ID" \
          -H 'Content-Type: application/json' \
          -H 'Accept: application/json;api-version=6.0-preview.1' \
          -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
          -d '{"size": '"$(stat --format="%s" $FILE)"'}'
        """

        check.state(os.path.isfile(in_file))

        file_size = os.stat(in_file).st_size

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=key,
            cache_size=file_size,
        )
        reserve_cmd = self.build_post_json_curl_cmd(
            'caches',
            GithubCacheServiceV1.dataclass_to_json(reserve_req),
        )
        reserve_resp_obj: ta.Any = check.not_none(self.run_json_curl_cmd(
            reserve_cmd,
            success_status_codes=[201],
        ))
        reserve_resp = GithubCacheServiceV1.dataclass_from_json(  # noqa
            reserve_resp_obj,
            GithubCacheServiceV1.ReserveCacheResponse,
        )

        raise NotImplementedError


##


class GithubShellCache(ShellCache):
    def __init__(
            self,
            dir: str,  # noqa
            *,
            client: ta.Optional[GithubV1CacheShellClient] = None,
    ) -> None:
        super().__init__()

        self._dir = check.not_none(dir)

        if client is None:
            client = GithubV1CacheShellClient()
        self._client = client

        self._local = DirectoryFileCache(self._dir)

    def get_file_cmd(self, key: str) -> ta.Optional[ShellCmd]:
        local_file = self._local.get_cache_file_path(key)
        if os.path.exists(local_file):
            return ShellCmd(f'cat {shlex.quote(local_file)}')

        if (entry := self._client.run_get_entry(key)) is None:
            return None

        tmp_file = self._local.format_incomplete_file(local_file)
        try:
            self._client.download_get_entry(entry, tmp_file)

            os.replace(tmp_file, local_file)

        except BaseException:  # noqa
            os.unlink(tmp_file)

            raise

        return ShellCmd(f'cat {shlex.quote(local_file)}')

    class _PutFileCmdContext(ShellCache.PutFileCmdContext):  # noqa
        def __init__(
                self,
                owner: 'GithubShellCache',
                key: str,
                tmp_file: str,
                local_file: str,
        ) -> None:
            super().__init__()

            self._owner = owner
            self._key = key
            self._tmp_file = tmp_file
            self._local_file = local_file

        @property
        def cmd(self) -> ShellCmd:
            return ShellCmd(f'cat > {shlex.quote(self._tmp_file)}')

        def _commit(self) -> None:
            os.replace(self._tmp_file, self._local_file)

            self._owner._client.upload_cache_entry(self._key, self._local_file)  # noqa

        def _abort(self) -> None:
            os.unlink(self._tmp_file)

    def put_file_cmd(self, key: str) -> ShellCache.PutFileCmdContext:
        local_file = self._local.get_cache_file_path(key, make_dirs=True)
        return self._PutFileCmdContext(
            self,
            key,
            self._local.format_incomplete_file(local_file),
            local_file,
        )
