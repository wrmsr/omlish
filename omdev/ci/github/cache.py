# ruff: noqa: UP006 UP007
# @omlish-lite
import os
import typing as ta

from omlish.lite.check import check

from ..cache import FileCache
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

    def build_headers(
            self,
            *,
            content_type: ta.Optional[str] = None,
    ) -> ta.Dict[str, str]:
        dct = {
            'Accept': f'application/json;{GithubCacheServiceV1.API_VERSION}',
        }

        if self._auth_token:
            dct['Authorization'] = f'Bearer {self._auth_token}'

        if content_type is not None:
            dct['Content-Type'] = content_type

        return dct

    def get_cmd(self) -> GithubCacheServiceV1.ArtifactCacheEntry:
        """
        curl \
          -X GET \
          "${ACTIONS_CACHE_URL}_apis/artifactcache/cache?keys=$CACHE_KEY" \
          -H 'Content-Type: application/json' \
          -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
          | jq .
        """
        raise NotImplementedError


##


class GithubV1FileCache(FileCache):
    def __init__(self, client: GithubV1CacheShellClient) -> None:
        super().__init__()

        self._client = client

    def get_file(self, key: str) -> ta.Optional[str]:
        raise NotImplementedError

    def put_file(self, key: str, file_path: str) -> ta.Optional[str]:
        raise NotImplementedError
