# ruff: noqa: UP006 UP007 UP045
"""
https://github.com/tonistiigi/go-actions-cache/blob/3e9a6642607fd6e4d5d4fdab7c91fe8bf4c36a25/cache_v2.go

==

curl -s \
  -X POST \
  "${ACTIONS_RESULTS_URL}twirp/github.actions.results.api.v1.CacheService/CreateCacheEntry" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "foo", "version": "0000000000000000000000000000000000000000000000000000000000000001" }' \
  | jq .

curl -s \
  -X POST \
  "${ACTIONS_RESULTS_URL}twirp/github.actions.results.api.v1.CacheService/GetCacheEntryDownloadURL" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "foo", "restoreKeys": [], "version": "0000000000000000000000000000000000000000000000000000000000000001" }' \
  | jq .

"""  # noqa
import dataclasses as dc
import typing as ta

from omlish.lite.check import check


T = ta.TypeVar('T')

GithubCacheServiceV2RequestT = ta.TypeVar('GithubCacheServiceV2RequestT')
GithubCacheServiceV2ResponseT = ta.TypeVar('GithubCacheServiceV2ResponseT')


##


class GithubCacheServiceV2:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    SERVICE_NAME = 'github.actions.results.api.v1.CacheService'

    @classmethod
    def get_service_url(cls, base_url: str) -> str:
        return f'{base_url.rstrip("/")}/twirp/{cls.SERVICE_NAME}'

    #

    @dc.dataclass(frozen=True)
    class Method(ta.Generic[GithubCacheServiceV2RequestT, GithubCacheServiceV2ResponseT]):
        name: str
        request: ta.Type[GithubCacheServiceV2RequestT]
        response: ta.Type[GithubCacheServiceV2ResponseT]

    #

    class CacheScopePermission:
        READ = 1
        WRITE = 2
        ALL = READ | WRITE

    @dc.dataclass(frozen=True)
    class CacheScope:
        scope: str
        permission: int  # CacheScopePermission

    @dc.dataclass(frozen=True)
    class CacheMetadata:
        repository_id: int
        scope: ta.Sequence['GithubCacheServiceV2.CacheScope']

    VERSION_LENGTH: int = 64

    #

    @dc.dataclass(frozen=True)
    class CreateCacheEntryRequest:
        key: str
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

        def __post_init__(self) -> None:
            check.equal(len(self.version), GithubCacheServiceV2.VERSION_LENGTH)

    @dc.dataclass(frozen=True)
    class CreateCacheEntryResponse:
        ok: bool
        signed_upload_url: str
        message: ta.Optional[str] = None

    CREATE_CACHE_ENTRY_METHOD: Method[
        CreateCacheEntryRequest,
        CreateCacheEntryResponse,
    ] = Method(
        'CreateCacheEntry',
        CreateCacheEntryRequest,
        CreateCacheEntryResponse,
    )

    #

    @dc.dataclass(frozen=True)
    class FinalizeCacheEntryUploadRequest:
        key: str
        size_bytes: int
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

    @dc.dataclass(frozen=True)
    class FinalizeCacheEntryUploadResponse:
        ok: bool
        entry_id: str
        message: ta.Optional[str] = None

    FINALIZE_CACHE_ENTRY_METHOD: Method[
        FinalizeCacheEntryUploadRequest,
        FinalizeCacheEntryUploadResponse,
    ] = Method(
        'FinalizeCacheEntryUpload',
        FinalizeCacheEntryUploadRequest,
        FinalizeCacheEntryUploadResponse,
    )

    #

    @dc.dataclass(frozen=True)
    class GetCacheEntryDownloadUrlRequest:
        key: str
        restore_keys: ta.Sequence[str]
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

    @dc.dataclass(frozen=True)
    class GetCacheEntryDownloadUrlResponse:
        ok: bool
        signed_download_url: str
        matched_key: str

    GET_CACHE_ENTRY_DOWNLOAD_URL_METHOD: Method[
        GetCacheEntryDownloadUrlRequest,
        GetCacheEntryDownloadUrlResponse,
    ] = Method(
        'GetCacheEntryDownloadURL',
        GetCacheEntryDownloadUrlRequest,
        GetCacheEntryDownloadUrlResponse,
    )
