# ruff: noqa: UP006 UP007
"""
export FILE_SIZE=$(stat --format="%s" $FILE)

export CACHE_ID=$(curl -s \
  -X POST \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "'"$CACHE_KEY"'", "cacheSize": '"$FILE_SIZE"'}' \
  | jq .cacheId)

curl -s \
  -X PATCH \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches/$CACHE_ID" \
  -H 'Content-Type: application/octet-stream' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -H "Content-Range: bytes 0-$((FILE_SIZE - 1))/*" \
  --data-binary @"$FILE"

curl -s \
  -X POST \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches/$CACHE_ID" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"size": '"$(stat --format="%s" $FILE)"'}'

curl -s \
  -X GET \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/cache?keys=$CACHE_KEY" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  | jq .
"""
import dataclasses as dc
import typing as ta

from omlish.lite.strings import camel_case
from omlish.lite.strings import snake_case


T = ta.TypeVar('T')


##


class GithubCacheServiceV1:
    API_VERSION = '6.0-preview.1'

    @classmethod
    def get_service_url(cls, base_url: str) -> str:
        return f'{base_url.rstrip("/")}/_apis/artifactcache'

    #

    @classmethod
    def dataclass_to_json(cls, obj: ta.Any) -> ta.Any:
        return {
            camel_case(k, lower=True): v
            for k, v in dc.asdict(obj).items()
            if v is not None
        }

    @classmethod
    def dataclass_from_json(cls, dcls: ta.Type[T], obj: ta.Any) -> T:
        return dcls(**{
            snake_case(k): v
            for k, v in obj.items()
        })

    #

    @dc.dataclass(frozen=True)
    class ArtifactCacheEntry:
        cache_key: ta.Optional[str]
        scope: ta.Optional[str]
        cache_version: ta.Optional[str]
        creation_time: ta.Optional[str]
        archive_location: ta.Optional[str]

    @dc.dataclass(frozen=True)
    class ArtifactCacheList:
        total_count: int
        artifact_caches: ta.Optional[ta.Sequence['GithubCacheServiceV1.ArtifactCacheEntry']]

    #

    @dc.dataclass(frozen=True)
    class ReserveCacheRequest:
        key: str
        cache_size: ta.Optional[int] = None
        version: ta.Optional[str] = None

    @dc.dataclass(frozen=True)
    class ReserveCacheResponse:
        cache_id: int

    #

    @dc.dataclass(frozen=True)
    class CommitCacheRequest:
        size: int

    #

    class CompressionMethod:
        GZIP = 'gzip'
        ZSTD_WITHOUT_LONG = 'zstd-without-long'
        ZSTD = 'zstd'

    @dc.dataclass(frozen=True)
    class InternalCacheOptions:
        compression_method: ta.Optional[str]  # CompressionMethod
        enable_cross_os_archive: ta.Optional[bool]
        cache_size: ta.Optional[int]


class GithubCacheServiceV2:
    SERVICE_NAME = 'github.actions.results.api.v1.CacheService'

    @dc.dataclass(frozen=True)
    class Method:
        name: str
        request: type
        response: type

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

    #

    @dc.dataclass(frozen=True)
    class CreateCacheEntryRequest:
        key: str
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

    @dc.dataclass(frozen=True)
    class CreateCacheEntryResponse:
        ok: bool
        signed_upload_url: str

    CREATE_CACHE_ENTRY_METHOD = Method(
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

    FINALIZE_CACHE_ENTRY_METHOD = Method(
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

    GET_CACHE_ENTRY_DOWNLOAD_URL_METHOD = Method(
        'GetCacheEntryDownloadURL',
        GetCacheEntryDownloadUrlRequest,
        GetCacheEntryDownloadUrlResponse,
    )
