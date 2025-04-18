# ruff: noqa: UP006 UP007
import abc
import asyncio
import dataclasses as dc
import http.client
import json
import typing as ta
import urllib.parse
import urllib.request

from omlish.lite.check import check
from omlish.lite.json import json_dumps_compact

from ...consts import CI_CACHE_VERSION
from ..env import register_github_env_var


##


class GithubCacheClient(abc.ABC):
    @dc.dataclass(frozen=True)
    class Entry(abc.ABC):  # noqa
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


class BaseGithubCacheClient(GithubCacheClient, abc.ABC):
    AUTH_TOKEN_ENV_VAR = register_github_env_var('ACTIONS_RUNTIME_TOKEN')  # noqa

    KEY_SUFFIX_ENV_VAR = register_github_env_var('GITHUB_RUN_ID')

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

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if (loop := self._given_loop) is not None:
            return loop
        return asyncio.get_running_loop()

    #

    def build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            *,
            content_type: ta.Optional[str] = None,
            json_content: bool = False,
    ) -> ta.Dict[str, str]:
        dct = {}

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

    async def send_url_request(
            self,
            req: urllib.request.Request,
    ) -> ta.Tuple[http.client.HTTPResponse, ta.Optional[bytes]]:
        def run_sync():
            with urllib.request.urlopen(req) as resp:  # noqa
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

    async def send_service_request(
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

        #

        req = urllib.request.Request(  # noqa
            url,
            method=method,
            headers=self.build_request_headers(
                headers,
                content_type=content_type,
                json_content=header_json_content,
            ),
            data=content,
        )

        resp, body = await self.send_url_request(req)

        #

        if success_status_codes is not None:
            is_success = resp.status in success_status_codes
        else:
            is_success = (200 <= resp.status <= 300)
        if not is_success:
            raise self.ServiceRequestError(resp.status, body)

        return self.load_json_bytes(body)

    #

    KEY_PART_SEPARATOR = '---'

    def fix_key(self, s: str, partial_suffix: bool = False) -> str:
        return self.KEY_PART_SEPARATOR.join([
            *([self._key_prefix] if self._key_prefix else []),
            s,
            ('' if partial_suffix else self._key_suffix),
        ])
