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

from ..shell import ShellCmd
from ..utils import make_temp_file


##


class GithubServiceCurlClient:
    def __init__(
            self,
            service_url: str,
            auth_token: ta.Optional[str] = None,
            *,
            api_version: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._service_url = check.non_empty_str(service_url)
        self._auth_token = auth_token
        self._api_version = api_version

    #

    _MISSING = object()

    def build_headers(
            self,
            *,
            auth_token: ta.Any = _MISSING,
            content_type: ta.Optional[str] = None,
    ) -> ta.Dict[str, str]:
        dct = {
            'Accept': ';'.join([
                'application/json',
                *([f'api-version={self._api_version}'] if self._api_version else []),
            ]),
        }

        if auth_token is self._MISSING:
            auth_token = self._auth_token
        if auth_token:
            dct['Authorization'] = f'Bearer {auth_token}'

        if content_type is not None:
            dct['Content-Type'] = content_type

        return dct

    #

    HEADER_AUTH_TOKEN_ENV_KEY_PREFIX = '_GITHUB_SERVICE_AUTH_TOKEN'  # noqa

    @property
    def header_auth_token_env_key(self) -> str:
        return f'{self.HEADER_AUTH_TOKEN_ENV_KEY_PREFIX}_{id(self)}'

    def build_cmd(
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
            header_env_key = self.header_auth_token_env_key
            env[header_env_key] = self._auth_token
            header_auth_token = f'${header_env_key}'
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

    def build_post_json_cmd(
            self,
            url: str,
            obj: ta.Any,
            **kwargs: ta.Any,
    ) -> ShellCmd:
        curl_cmd = self.build_cmd(
            'POST',
            url,
            json_content=True,
            **kwargs,
        )

        obj_json = json_dumps_compact(obj)

        return dc.replace(curl_cmd, s=f'{curl_cmd.s} -d {shlex.quote(obj_json)}')

    #

    @dc.dataclass()
    class Error(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

        def __str__(self) -> str:
            return repr(self)

    @dc.dataclass(frozen=True)
    class Result:
        status_code: int
        body: ta.Optional[bytes]

        def as_error(self) -> 'GithubServiceCurlClient.Error':
            return GithubServiceCurlClient.Error(
                status_code=self.status_code,
                body=self.body,
            )

    def run_cmd(
            self,
            cmd: ShellCmd,
            *,
            raise_: bool = False,
    ) -> Result:
        out_file = make_temp_file()
        with defer(lambda: os.unlink(out_file)):
            run_cmd = dc.replace(cmd, s=f"{cmd.s} -o {out_file} -w '%{{json}}'")

            out_json_bytes = run_cmd.run(subprocesses.check_output)

            out_json = json.loads(out_json_bytes.decode())
            status_code = check.isinstance(out_json['response_code'], int)

            with open(out_file, 'rb') as f:
                body = f.read()

            result = self.Result(
                status_code=status_code,
                body=body,
            )

        if raise_ and (500 <= status_code <= 600):
            raise result.as_error()

        return result

    def run_json_cmd(
            self,
            cmd: ShellCmd,
            *,
            success_status_codes: ta.Optional[ta.Container[int]] = None,
    ) -> ta.Optional[ta.Any]:
        result = self.run_cmd(cmd, raise_=True)

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
