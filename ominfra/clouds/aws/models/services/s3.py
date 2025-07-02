# flake8: noqa: E501
# ruff: noqa: N801 S105
# fmt: off
# @omlish-generated
import enum as _enum  # noqa
import typing as _ta  # noqa

from omlish import dataclasses as _dc  # noqa

from .. import base as _base  # noqa


##


AcceptRanges = _ta.NewType('AcceptRanges', str)

AccountId = _ta.NewType('AccountId', str)

Body = _ta.NewType('Body', bytes)

BucketKeyEnabled = _ta.NewType('BucketKeyEnabled', bool)

BucketName = _ta.NewType('BucketName', str)

BucketRegion = _ta.NewType('BucketRegion', str)

BypassGovernanceRetention = _ta.NewType('BypassGovernanceRetention', bool)

CacheControl = _ta.NewType('CacheControl', str)


class ChecksumAlgorithm(_enum.Enum):
    CRC32 = 'CRC32'
    CRC32C = 'CRC32C'
    SHA1 = 'SHA1'
    SHA256 = 'SHA256'
    CRC64NVME = 'CRC64NVME'


ChecksumCRC32 = _ta.NewType('ChecksumCRC32', str)

ChecksumCRC32C = _ta.NewType('ChecksumCRC32C', str)

ChecksumCRC64NVME = _ta.NewType('ChecksumCRC64NVME', str)


class ChecksumMode(_enum.Enum):
    ENABLED = 'ENABLED'


ChecksumSHA1 = _ta.NewType('ChecksumSHA1', str)

ChecksumSHA256 = _ta.NewType('ChecksumSHA256', str)


class ChecksumType(_enum.Enum):
    COMPOSITE = 'COMPOSITE'
    FULL_OBJECT = 'FULL_OBJECT'


ContentDisposition = _ta.NewType('ContentDisposition', str)

ContentEncoding = _ta.NewType('ContentEncoding', str)

ContentLanguage = _ta.NewType('ContentLanguage', str)

ContentLength = _ta.NewType('ContentLength', int)

ContentMD5 = _ta.NewType('ContentMD5', str)

ContentRange = _ta.NewType('ContentRange', str)

ContentType = _ta.NewType('ContentType', str)

CreationDate = _ta.NewType('CreationDate', _base.Timestamp)

DeleteMarker = _ta.NewType('DeleteMarker', bool)

Delimiter = _ta.NewType('Delimiter', str)

DisplayName = _ta.NewType('DisplayName', str)

ETag = _ta.NewType('ETag', str)


class EncodingType(_enum.Enum):
    URL = 'url'


@_dc.dataclass(frozen=True, kw_only=True)
class EncryptionTypeMismatch(
    _base.Shape,
    shape_name='EncryptionTypeMismatch',
):
    pass


Expiration = _ta.NewType('Expiration', str)

Expires = _ta.NewType('Expires', _base.Timestamp)

FetchOwner = _ta.NewType('FetchOwner', bool)

GrantFullControl = _ta.NewType('GrantFullControl', str)

GrantRead = _ta.NewType('GrantRead', str)

GrantReadACP = _ta.NewType('GrantReadACP', str)

GrantWriteACP = _ta.NewType('GrantWriteACP', str)

ID = _ta.NewType('ID', str)

IfMatch = _ta.NewType('IfMatch', str)

IfMatchLastModifiedTime = _ta.NewType('IfMatchLastModifiedTime', _base.Timestamp)

IfMatchSize = _ta.NewType('IfMatchSize', int)

IfModifiedSince = _ta.NewType('IfModifiedSince', _base.Timestamp)

IfNoneMatch = _ta.NewType('IfNoneMatch', str)

IfUnmodifiedSince = _ta.NewType('IfUnmodifiedSince', _base.Timestamp)


class IntelligentTieringAccessTier(_enum.Enum):
    ARCHIVE_ACCESS = 'ARCHIVE_ACCESS'
    DEEP_ARCHIVE_ACCESS = 'DEEP_ARCHIVE_ACCESS'


@_dc.dataclass(frozen=True, kw_only=True)
class InvalidRequest(
    _base.Shape,
    shape_name='InvalidRequest',
):
    pass


@_dc.dataclass(frozen=True, kw_only=True)
class InvalidWriteOffset(
    _base.Shape,
    shape_name='InvalidWriteOffset',
):
    pass


IsRestoreInProgress = _ta.NewType('IsRestoreInProgress', bool)

IsTruncated = _ta.NewType('IsTruncated', bool)

KeyCount = _ta.NewType('KeyCount', int)

LastModified = _ta.NewType('LastModified', _base.Timestamp)

MFA = _ta.NewType('MFA', str)

MaxBuckets = _ta.NewType('MaxBuckets', int)

MaxKeys = _ta.NewType('MaxKeys', int)

MetadataKey = _ta.NewType('MetadataKey', str)

MetadataValue = _ta.NewType('MetadataValue', str)

MissingMeta = _ta.NewType('MissingMeta', int)

NextToken = _ta.NewType('NextToken', str)


@_dc.dataclass(frozen=True, kw_only=True)
class NoSuchBucket(
    _base.Shape,
    shape_name='NoSuchBucket',
):
    pass


@_dc.dataclass(frozen=True, kw_only=True)
class NoSuchKey(
    _base.Shape,
    shape_name='NoSuchKey',
):
    pass


class ObjectCannedACL(_enum.Enum):
    PRIVATE = 'private'
    PUBLIC_READ = 'public-read'
    PUBLIC_READ_WRITE = 'public-read-write'
    AUTHENTICATED_READ = 'authenticated-read'
    AWS_EXEC_READ = 'aws-exec-read'
    BUCKET_OWNER_READ = 'bucket-owner-read'
    BUCKET_OWNER_FULL_CONTROL = 'bucket-owner-full-control'


ObjectKey = _ta.NewType('ObjectKey', str)


class ObjectLockLegalHoldStatus(_enum.Enum):
    ON = 'ON'
    OFF = 'OFF'


class ObjectLockMode(_enum.Enum):
    GOVERNANCE = 'GOVERNANCE'
    COMPLIANCE = 'COMPLIANCE'


ObjectLockRetainUntilDate = _ta.NewType('ObjectLockRetainUntilDate', _base.Timestamp)


class ObjectStorageClass(_enum.Enum):
    STANDARD = 'STANDARD'
    REDUCED_REDUNDANCY = 'REDUCED_REDUNDANCY'
    GLACIER = 'GLACIER'
    STANDARD_IA = 'STANDARD_IA'
    ONEZONE_IA = 'ONEZONE_IA'
    INTELLIGENT_TIERING = 'INTELLIGENT_TIERING'
    DEEP_ARCHIVE = 'DEEP_ARCHIVE'
    OUTPOSTS = 'OUTPOSTS'
    GLACIER_IR = 'GLACIER_IR'
    SNOW = 'SNOW'
    EXPRESS_ONEZONE = 'EXPRESS_ONEZONE'
    FSX_OPENZFS = 'FSX_OPENZFS'


ObjectVersionId = _ta.NewType('ObjectVersionId', str)


class OptionalObjectAttributes(_enum.Enum):
    RESTORE_STATUS = 'RestoreStatus'


PartNumber = _ta.NewType('PartNumber', int)

PartsCount = _ta.NewType('PartsCount', int)

Prefix = _ta.NewType('Prefix', str)

Range = _ta.NewType('Range', str)


class ReplicationStatus(_enum.Enum):
    COMPLETE = 'COMPLETE'
    PENDING = 'PENDING'
    FAILED = 'FAILED'
    REPLICA = 'REPLICA'
    COMPLETED = 'COMPLETED'


class RequestCharged(_enum.Enum):
    REQUESTER = 'requester'


class RequestPayer(_enum.Enum):
    REQUESTER = 'requester'


ResponseCacheControl = _ta.NewType('ResponseCacheControl', str)

ResponseContentDisposition = _ta.NewType('ResponseContentDisposition', str)

ResponseContentEncoding = _ta.NewType('ResponseContentEncoding', str)

ResponseContentLanguage = _ta.NewType('ResponseContentLanguage', str)

ResponseContentType = _ta.NewType('ResponseContentType', str)

ResponseExpires = _ta.NewType('ResponseExpires', _base.Timestamp)

Restore = _ta.NewType('Restore', str)

RestoreExpiryDate = _ta.NewType('RestoreExpiryDate', _base.Timestamp)

S3RegionalOrS3ExpressBucketArnString = _ta.NewType('S3RegionalOrS3ExpressBucketArnString', str)

SSECustomerAlgorithm = _ta.NewType('SSECustomerAlgorithm', str)

SSECustomerKey = _ta.NewType('SSECustomerKey', str)

SSECustomerKeyMD5 = _ta.NewType('SSECustomerKeyMD5', str)

SSEKMSEncryptionContext = _ta.NewType('SSEKMSEncryptionContext', str)

SSEKMSKeyId = _ta.NewType('SSEKMSKeyId', str)


class ServerSideEncryption(_enum.Enum):
    AES256 = 'AES256'
    AWS_FSX = 'aws:fsx'
    AWS_KMS = 'aws:kms'
    AWS_KMS_DSSE = 'aws:kms:dsse'


Size = _ta.NewType('Size', int)

StartAfter = _ta.NewType('StartAfter', str)


class StorageClass(_enum.Enum):
    STANDARD = 'STANDARD'
    REDUCED_REDUNDANCY = 'REDUCED_REDUNDANCY'
    STANDARD_IA = 'STANDARD_IA'
    ONEZONE_IA = 'ONEZONE_IA'
    INTELLIGENT_TIERING = 'INTELLIGENT_TIERING'
    GLACIER = 'GLACIER'
    DEEP_ARCHIVE = 'DEEP_ARCHIVE'
    OUTPOSTS = 'OUTPOSTS'
    GLACIER_IR = 'GLACIER_IR'
    SNOW = 'SNOW'
    EXPRESS_ONEZONE = 'EXPRESS_ONEZONE'
    FSX_OPENZFS = 'FSX_OPENZFS'


TagCount = _ta.NewType('TagCount', int)

TaggingHeader = _ta.NewType('TaggingHeader', str)

Token = _ta.NewType('Token', str)


@_dc.dataclass(frozen=True, kw_only=True)
class TooManyParts(
    _base.Shape,
    shape_name='TooManyParts',
):
    pass


WebsiteRedirectLocation = _ta.NewType('WebsiteRedirectLocation', str)

WriteOffsetBytes = _ta.NewType('WriteOffsetBytes', int)


@_dc.dataclass(frozen=True, kw_only=True)
class Bucket(
    _base.Shape,
    shape_name='Bucket',
):
    name: BucketName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        shape_name='BucketName',
    ))

    creation_date: CreationDate | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CreationDate',
        shape_name='CreationDate',
    ))

    bucket_region: BucketRegion | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BucketRegion',
        shape_name='BucketRegion',
    ))

    bucket_arn: S3RegionalOrS3ExpressBucketArnString | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BucketArn',
        shape_name='S3RegionalOrS3ExpressBucketArnString',
    ))


ChecksumAlgorithmList: _ta.TypeAlias = _ta.Sequence[ChecksumAlgorithm]


@_dc.dataclass(frozen=True, kw_only=True)
class CommonPrefix(
    _base.Shape,
    shape_name='CommonPrefix',
):
    prefix: Prefix | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Prefix',
        shape_name='Prefix',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DeleteObjectOutput(
    _base.Shape,
    shape_name='DeleteObjectOutput',
):
    delete_marker: DeleteMarker | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeleteMarker',
        serialization_name='x-amz-delete-marker',
        shape_name='DeleteMarker',
    ))

    version_id: ObjectVersionId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VersionId',
        serialization_name='x-amz-version-id',
        shape_name='ObjectVersionId',
    ))

    request_charged: RequestCharged | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequestCharged',
        serialization_name='x-amz-request-charged',
        shape_name='RequestCharged',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DeleteObjectRequest(
    _base.Shape,
    shape_name='DeleteObjectRequest',
):
    bucket: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Bucket',
        serialization_name='Bucket',
        shape_name='BucketName',
    ))

    key: ObjectKey = _dc.field(metadata=_base.field_metadata(
        member_name='Key',
        serialization_name='Key',
        shape_name='ObjectKey',
    ))

    mfa: MFA | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MFA',
        serialization_name='x-amz-mfa',
        shape_name='MFA',
    ))

    version_id: ObjectVersionId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VersionId',
        serialization_name='versionId',
        shape_name='ObjectVersionId',
    ))

    request_payer: RequestPayer | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequestPayer',
        serialization_name='x-amz-request-payer',
        shape_name='RequestPayer',
    ))

    bypass_governance_retention: BypassGovernanceRetention | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BypassGovernanceRetention',
        serialization_name='x-amz-bypass-governance-retention',
        shape_name='BypassGovernanceRetention',
    ))

    expected_bucket_owner: AccountId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ExpectedBucketOwner',
        serialization_name='x-amz-expected-bucket-owner',
        shape_name='AccountId',
    ))

    if_match: IfMatch | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfMatch',
        serialization_name='If-Match',
        shape_name='IfMatch',
    ))

    if_match_last_modified_time: IfMatchLastModifiedTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfMatchLastModifiedTime',
        serialization_name='x-amz-if-match-last-modified-time',
        shape_name='IfMatchLastModifiedTime',
    ))

    if_match_size: IfMatchSize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfMatchSize',
        serialization_name='x-amz-if-match-size',
        shape_name='IfMatchSize',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class GetObjectRequest(
    _base.Shape,
    shape_name='GetObjectRequest',
):
    bucket: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Bucket',
        serialization_name='Bucket',
        shape_name='BucketName',
    ))

    if_match: IfMatch | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfMatch',
        serialization_name='If-Match',
        shape_name='IfMatch',
    ))

    if_modified_since: IfModifiedSince | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfModifiedSince',
        serialization_name='If-Modified-Since',
        shape_name='IfModifiedSince',
    ))

    if_none_match: IfNoneMatch | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfNoneMatch',
        serialization_name='If-None-Match',
        shape_name='IfNoneMatch',
    ))

    if_unmodified_since: IfUnmodifiedSince | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfUnmodifiedSince',
        serialization_name='If-Unmodified-Since',
        shape_name='IfUnmodifiedSince',
    ))

    key: ObjectKey = _dc.field(metadata=_base.field_metadata(
        member_name='Key',
        serialization_name='Key',
        shape_name='ObjectKey',
    ))

    range: Range | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Range',
        serialization_name='Range',
        shape_name='Range',
    ))

    response_cache_control: ResponseCacheControl | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ResponseCacheControl',
        serialization_name='response-cache-control',
        shape_name='ResponseCacheControl',
    ))

    response_content_disposition: ResponseContentDisposition | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ResponseContentDisposition',
        serialization_name='response-content-disposition',
        shape_name='ResponseContentDisposition',
    ))

    response_content_encoding: ResponseContentEncoding | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ResponseContentEncoding',
        serialization_name='response-content-encoding',
        shape_name='ResponseContentEncoding',
    ))

    response_content_language: ResponseContentLanguage | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ResponseContentLanguage',
        serialization_name='response-content-language',
        shape_name='ResponseContentLanguage',
    ))

    response_content_type: ResponseContentType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ResponseContentType',
        serialization_name='response-content-type',
        shape_name='ResponseContentType',
    ))

    response_expires: ResponseExpires | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ResponseExpires',
        serialization_name='response-expires',
        shape_name='ResponseExpires',
    ))

    version_id: ObjectVersionId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VersionId',
        serialization_name='versionId',
        shape_name='ObjectVersionId',
    ))

    sse_customer_algorithm: SSECustomerAlgorithm | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerAlgorithm',
        serialization_name='x-amz-server-side-encryption-customer-algorithm',
        shape_name='SSECustomerAlgorithm',
    ))

    sse_customer_key: SSECustomerKey | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerKey',
        serialization_name='x-amz-server-side-encryption-customer-key',
        shape_name='SSECustomerKey',
    ))

    sse_customer_key_md5: SSECustomerKeyMD5 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerKeyMD5',
        serialization_name='x-amz-server-side-encryption-customer-key-MD5',
        shape_name='SSECustomerKeyMD5',
    ))

    request_payer: RequestPayer | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequestPayer',
        serialization_name='x-amz-request-payer',
        shape_name='RequestPayer',
    ))

    part_number: PartNumber | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PartNumber',
        serialization_name='partNumber',
        shape_name='PartNumber',
    ))

    expected_bucket_owner: AccountId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ExpectedBucketOwner',
        serialization_name='x-amz-expected-bucket-owner',
        shape_name='AccountId',
    ))

    checksum_mode: ChecksumMode | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumMode',
        serialization_name='x-amz-checksum-mode',
        shape_name='ChecksumMode',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InvalidObjectState(
    _base.Shape,
    shape_name='InvalidObjectState',
):
    storage_class: StorageClass | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StorageClass',
        shape_name='StorageClass',
    ))

    access_tier: IntelligentTieringAccessTier | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AccessTier',
        shape_name='IntelligentTieringAccessTier',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ListBucketsRequest(
    _base.Shape,
    shape_name='ListBucketsRequest',
):
    max_buckets: MaxBuckets | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxBuckets',
        serialization_name='max-buckets',
        shape_name='MaxBuckets',
    ))

    continuation_token: Token | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContinuationToken',
        serialization_name='continuation-token',
        shape_name='Token',
    ))

    prefix: Prefix | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Prefix',
        serialization_name='prefix',
        shape_name='Prefix',
    ))

    bucket_region: BucketRegion | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BucketRegion',
        serialization_name='bucket-region',
        shape_name='BucketRegion',
    ))


Metadata: _ta.TypeAlias = _ta.Mapping[MetadataKey, MetadataKey]

OptionalObjectAttributesList: _ta.TypeAlias = _ta.Sequence[OptionalObjectAttributes]


@_dc.dataclass(frozen=True, kw_only=True)
class Owner(
    _base.Shape,
    shape_name='Owner',
):
    display_name: DisplayName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DisplayName',
        shape_name='DisplayName',
    ))

    i_d: ID | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ID',
        shape_name='ID',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class PutObjectOutput(
    _base.Shape,
    shape_name='PutObjectOutput',
):
    expiration: Expiration | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Expiration',
        serialization_name='x-amz-expiration',
        shape_name='Expiration',
    ))

    etag: ETag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ETag',
        serialization_name='ETag',
        shape_name='ETag',
    ))

    checksum_crc32: ChecksumCRC32 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC32',
        serialization_name='x-amz-checksum-crc32',
        shape_name='ChecksumCRC32',
    ))

    checksum_crc32c: ChecksumCRC32C | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC32C',
        serialization_name='x-amz-checksum-crc32c',
        shape_name='ChecksumCRC32C',
    ))

    checksum_crc64_nvme: ChecksumCRC64NVME | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC64NVME',
        serialization_name='x-amz-checksum-crc64nvme',
        shape_name='ChecksumCRC64NVME',
    ))

    checksum_sha1: ChecksumSHA1 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumSHA1',
        serialization_name='x-amz-checksum-sha1',
        shape_name='ChecksumSHA1',
    ))

    checksum_sha256: ChecksumSHA256 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumSHA256',
        serialization_name='x-amz-checksum-sha256',
        shape_name='ChecksumSHA256',
    ))

    checksum_type: ChecksumType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumType',
        serialization_name='x-amz-checksum-type',
        shape_name='ChecksumType',
    ))

    server_side_encryption: ServerSideEncryption | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ServerSideEncryption',
        serialization_name='x-amz-server-side-encryption',
        shape_name='ServerSideEncryption',
    ))

    version_id: ObjectVersionId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VersionId',
        serialization_name='x-amz-version-id',
        shape_name='ObjectVersionId',
    ))

    sse_customer_algorithm: SSECustomerAlgorithm | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerAlgorithm',
        serialization_name='x-amz-server-side-encryption-customer-algorithm',
        shape_name='SSECustomerAlgorithm',
    ))

    sse_customer_key_md5: SSECustomerKeyMD5 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerKeyMD5',
        serialization_name='x-amz-server-side-encryption-customer-key-MD5',
        shape_name='SSECustomerKeyMD5',
    ))

    sse_kms_key_id: SSEKMSKeyId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSEKMSKeyId',
        serialization_name='x-amz-server-side-encryption-aws-kms-key-id',
        shape_name='SSEKMSKeyId',
    ))

    sse_kms_encryption_context: SSEKMSEncryptionContext | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSEKMSEncryptionContext',
        serialization_name='x-amz-server-side-encryption-context',
        shape_name='SSEKMSEncryptionContext',
    ))

    bucket_key_enabled: BucketKeyEnabled | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BucketKeyEnabled',
        serialization_name='x-amz-server-side-encryption-bucket-key-enabled',
        shape_name='BucketKeyEnabled',
    ))

    size: Size | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Size',
        serialization_name='x-amz-object-size',
        shape_name='Size',
    ))

    request_charged: RequestCharged | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequestCharged',
        serialization_name='x-amz-request-charged',
        shape_name='RequestCharged',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class RestoreStatus(
    _base.Shape,
    shape_name='RestoreStatus',
):
    is_restore_in_progress: IsRestoreInProgress | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IsRestoreInProgress',
        shape_name='IsRestoreInProgress',
    ))

    restore_expiry_date: RestoreExpiryDate | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RestoreExpiryDate',
        shape_name='RestoreExpiryDate',
    ))


Buckets: _ta.TypeAlias = _ta.Sequence[Bucket]

CommonPrefixList: _ta.TypeAlias = _ta.Sequence[CommonPrefix]


@_dc.dataclass(frozen=True, kw_only=True)
class GetObjectOutput(
    _base.Shape,
    shape_name='GetObjectOutput',
):
    body: Body | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Body',
        shape_name='Body',
    ))

    delete_marker: DeleteMarker | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeleteMarker',
        serialization_name='x-amz-delete-marker',
        shape_name='DeleteMarker',
    ))

    accept_ranges: AcceptRanges | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AcceptRanges',
        serialization_name='accept-ranges',
        shape_name='AcceptRanges',
    ))

    expiration: Expiration | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Expiration',
        serialization_name='x-amz-expiration',
        shape_name='Expiration',
    ))

    restore: Restore | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Restore',
        serialization_name='x-amz-restore',
        shape_name='Restore',
    ))

    last_modified: LastModified | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LastModified',
        serialization_name='Last-Modified',
        shape_name='LastModified',
    ))

    content_length: ContentLength | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentLength',
        serialization_name='Content-Length',
        shape_name='ContentLength',
    ))

    etag: ETag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ETag',
        serialization_name='ETag',
        shape_name='ETag',
    ))

    checksum_crc32: ChecksumCRC32 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC32',
        serialization_name='x-amz-checksum-crc32',
        shape_name='ChecksumCRC32',
    ))

    checksum_crc32c: ChecksumCRC32C | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC32C',
        serialization_name='x-amz-checksum-crc32c',
        shape_name='ChecksumCRC32C',
    ))

    checksum_crc64_nvme: ChecksumCRC64NVME | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC64NVME',
        serialization_name='x-amz-checksum-crc64nvme',
        shape_name='ChecksumCRC64NVME',
    ))

    checksum_sha1: ChecksumSHA1 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumSHA1',
        serialization_name='x-amz-checksum-sha1',
        shape_name='ChecksumSHA1',
    ))

    checksum_sha256: ChecksumSHA256 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumSHA256',
        serialization_name='x-amz-checksum-sha256',
        shape_name='ChecksumSHA256',
    ))

    checksum_type: ChecksumType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumType',
        serialization_name='x-amz-checksum-type',
        shape_name='ChecksumType',
    ))

    missing_meta: MissingMeta | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MissingMeta',
        serialization_name='x-amz-missing-meta',
        shape_name='MissingMeta',
    ))

    version_id: ObjectVersionId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VersionId',
        serialization_name='x-amz-version-id',
        shape_name='ObjectVersionId',
    ))

    cache_control: CacheControl | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CacheControl',
        serialization_name='Cache-Control',
        shape_name='CacheControl',
    ))

    content_disposition: ContentDisposition | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentDisposition',
        serialization_name='Content-Disposition',
        shape_name='ContentDisposition',
    ))

    content_encoding: ContentEncoding | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentEncoding',
        serialization_name='Content-Encoding',
        shape_name='ContentEncoding',
    ))

    content_language: ContentLanguage | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentLanguage',
        serialization_name='Content-Language',
        shape_name='ContentLanguage',
    ))

    content_range: ContentRange | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentRange',
        serialization_name='Content-Range',
        shape_name='ContentRange',
    ))

    content_type: ContentType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentType',
        serialization_name='Content-Type',
        shape_name='ContentType',
    ))

    expires: Expires | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Expires',
        serialization_name='Expires',
        shape_name='Expires',
    ))

    website_redirect_location: WebsiteRedirectLocation | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='WebsiteRedirectLocation',
        serialization_name='x-amz-website-redirect-location',
        shape_name='WebsiteRedirectLocation',
    ))

    server_side_encryption: ServerSideEncryption | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ServerSideEncryption',
        serialization_name='x-amz-server-side-encryption',
        shape_name='ServerSideEncryption',
    ))

    metadata: Metadata | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Metadata',
        serialization_name='x-amz-meta-',
        value_type=_base.MapValueType(MetadataKey, MetadataValue),
        shape_name='Metadata',
    ))

    sse_customer_algorithm: SSECustomerAlgorithm | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerAlgorithm',
        serialization_name='x-amz-server-side-encryption-customer-algorithm',
        shape_name='SSECustomerAlgorithm',
    ))

    sse_customer_key_md5: SSECustomerKeyMD5 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerKeyMD5',
        serialization_name='x-amz-server-side-encryption-customer-key-MD5',
        shape_name='SSECustomerKeyMD5',
    ))

    sse_kms_key_id: SSEKMSKeyId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSEKMSKeyId',
        serialization_name='x-amz-server-side-encryption-aws-kms-key-id',
        shape_name='SSEKMSKeyId',
    ))

    bucket_key_enabled: BucketKeyEnabled | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BucketKeyEnabled',
        serialization_name='x-amz-server-side-encryption-bucket-key-enabled',
        shape_name='BucketKeyEnabled',
    ))

    storage_class: StorageClass | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StorageClass',
        serialization_name='x-amz-storage-class',
        shape_name='StorageClass',
    ))

    request_charged: RequestCharged | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequestCharged',
        serialization_name='x-amz-request-charged',
        shape_name='RequestCharged',
    ))

    replication_status: ReplicationStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ReplicationStatus',
        serialization_name='x-amz-replication-status',
        shape_name='ReplicationStatus',
    ))

    parts_count: PartsCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PartsCount',
        serialization_name='x-amz-mp-parts-count',
        shape_name='PartsCount',
    ))

    tag_count: TagCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TagCount',
        serialization_name='x-amz-tagging-count',
        shape_name='TagCount',
    ))

    object_lock_mode: ObjectLockMode | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ObjectLockMode',
        serialization_name='x-amz-object-lock-mode',
        shape_name='ObjectLockMode',
    ))

    object_lock_retain_until_date: ObjectLockRetainUntilDate | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ObjectLockRetainUntilDate',
        serialization_name='x-amz-object-lock-retain-until-date',
        shape_name='ObjectLockRetainUntilDate',
    ))

    object_lock_legal_hold_status: ObjectLockLegalHoldStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ObjectLockLegalHoldStatus',
        serialization_name='x-amz-object-lock-legal-hold',
        shape_name='ObjectLockLegalHoldStatus',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ListObjectsV2Request(
    _base.Shape,
    shape_name='ListObjectsV2Request',
):
    bucket: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Bucket',
        serialization_name='Bucket',
        shape_name='BucketName',
    ))

    delimiter: Delimiter | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Delimiter',
        serialization_name='delimiter',
        shape_name='Delimiter',
    ))

    encoding_type: EncodingType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EncodingType',
        serialization_name='encoding-type',
        shape_name='EncodingType',
    ))

    max_keys: MaxKeys | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxKeys',
        serialization_name='max-keys',
        shape_name='MaxKeys',
    ))

    prefix: Prefix | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Prefix',
        serialization_name='prefix',
        shape_name='Prefix',
    ))

    continuation_token: Token | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContinuationToken',
        serialization_name='continuation-token',
        shape_name='Token',
    ))

    fetch_owner: FetchOwner | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='FetchOwner',
        serialization_name='fetch-owner',
        shape_name='FetchOwner',
    ))

    start_after: StartAfter | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StartAfter',
        serialization_name='start-after',
        shape_name='StartAfter',
    ))

    request_payer: RequestPayer | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequestPayer',
        serialization_name='x-amz-request-payer',
        shape_name='RequestPayer',
    ))

    expected_bucket_owner: AccountId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ExpectedBucketOwner',
        serialization_name='x-amz-expected-bucket-owner',
        shape_name='AccountId',
    ))

    optional_object_attributes: OptionalObjectAttributesList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OptionalObjectAttributes',
        serialization_name='x-amz-optional-object-attributes',
        value_type=_base.ListValueType(OptionalObjectAttributes),
        shape_name='OptionalObjectAttributesList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Object(
    _base.Shape,
    shape_name='Object',
):
    key: ObjectKey | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Key',
        shape_name='ObjectKey',
    ))

    last_modified: LastModified | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LastModified',
        shape_name='LastModified',
    ))

    etag: ETag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ETag',
        shape_name='ETag',
    ))

    checksum_algorithm: ChecksumAlgorithmList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumAlgorithm',
        value_type=_base.ListValueType(ChecksumAlgorithm),
        shape_name='ChecksumAlgorithmList',
    ))

    checksum_type: ChecksumType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumType',
        shape_name='ChecksumType',
    ))

    size: Size | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Size',
        shape_name='Size',
    ))

    storage_class: ObjectStorageClass | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StorageClass',
        shape_name='ObjectStorageClass',
    ))

    owner: Owner | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Owner',
        shape_name='Owner',
    ))

    restore_status: RestoreStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RestoreStatus',
        shape_name='RestoreStatus',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class PutObjectRequest(
    _base.Shape,
    shape_name='PutObjectRequest',
):
    acl: ObjectCannedACL | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ACL',
        serialization_name='x-amz-acl',
        shape_name='ObjectCannedACL',
    ))

    body: Body | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Body',
        shape_name='Body',
    ))

    bucket: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Bucket',
        serialization_name='Bucket',
        shape_name='BucketName',
    ))

    cache_control: CacheControl | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CacheControl',
        serialization_name='Cache-Control',
        shape_name='CacheControl',
    ))

    content_disposition: ContentDisposition | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentDisposition',
        serialization_name='Content-Disposition',
        shape_name='ContentDisposition',
    ))

    content_encoding: ContentEncoding | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentEncoding',
        serialization_name='Content-Encoding',
        shape_name='ContentEncoding',
    ))

    content_language: ContentLanguage | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentLanguage',
        serialization_name='Content-Language',
        shape_name='ContentLanguage',
    ))

    content_length: ContentLength | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentLength',
        serialization_name='Content-Length',
        shape_name='ContentLength',
    ))

    content_md5: ContentMD5 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentMD5',
        serialization_name='Content-MD5',
        shape_name='ContentMD5',
    ))

    content_type: ContentType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContentType',
        serialization_name='Content-Type',
        shape_name='ContentType',
    ))

    checksum_algorithm: ChecksumAlgorithm | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumAlgorithm',
        serialization_name='x-amz-sdk-checksum-algorithm',
        shape_name='ChecksumAlgorithm',
    ))

    checksum_crc32: ChecksumCRC32 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC32',
        serialization_name='x-amz-checksum-crc32',
        shape_name='ChecksumCRC32',
    ))

    checksum_crc32c: ChecksumCRC32C | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC32C',
        serialization_name='x-amz-checksum-crc32c',
        shape_name='ChecksumCRC32C',
    ))

    checksum_crc64_nvme: ChecksumCRC64NVME | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumCRC64NVME',
        serialization_name='x-amz-checksum-crc64nvme',
        shape_name='ChecksumCRC64NVME',
    ))

    checksum_sha1: ChecksumSHA1 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumSHA1',
        serialization_name='x-amz-checksum-sha1',
        shape_name='ChecksumSHA1',
    ))

    checksum_sha256: ChecksumSHA256 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ChecksumSHA256',
        serialization_name='x-amz-checksum-sha256',
        shape_name='ChecksumSHA256',
    ))

    expires: Expires | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Expires',
        serialization_name='Expires',
        shape_name='Expires',
    ))

    if_match: IfMatch | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfMatch',
        serialization_name='If-Match',
        shape_name='IfMatch',
    ))

    if_none_match: IfNoneMatch | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IfNoneMatch',
        serialization_name='If-None-Match',
        shape_name='IfNoneMatch',
    ))

    grant_full_control: GrantFullControl | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GrantFullControl',
        serialization_name='x-amz-grant-full-control',
        shape_name='GrantFullControl',
    ))

    grant_read: GrantRead | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GrantRead',
        serialization_name='x-amz-grant-read',
        shape_name='GrantRead',
    ))

    grant_read_acp: GrantReadACP | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GrantReadACP',
        serialization_name='x-amz-grant-read-acp',
        shape_name='GrantReadACP',
    ))

    grant_write_acp: GrantWriteACP | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GrantWriteACP',
        serialization_name='x-amz-grant-write-acp',
        shape_name='GrantWriteACP',
    ))

    key: ObjectKey = _dc.field(metadata=_base.field_metadata(
        member_name='Key',
        serialization_name='Key',
        shape_name='ObjectKey',
    ))

    write_offset_bytes: WriteOffsetBytes | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='WriteOffsetBytes',
        serialization_name='x-amz-write-offset-bytes',
        shape_name='WriteOffsetBytes',
    ))

    metadata: Metadata | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Metadata',
        serialization_name='x-amz-meta-',
        value_type=_base.MapValueType(MetadataKey, MetadataValue),
        shape_name='Metadata',
    ))

    server_side_encryption: ServerSideEncryption | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ServerSideEncryption',
        serialization_name='x-amz-server-side-encryption',
        shape_name='ServerSideEncryption',
    ))

    storage_class: StorageClass | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StorageClass',
        serialization_name='x-amz-storage-class',
        shape_name='StorageClass',
    ))

    website_redirect_location: WebsiteRedirectLocation | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='WebsiteRedirectLocation',
        serialization_name='x-amz-website-redirect-location',
        shape_name='WebsiteRedirectLocation',
    ))

    sse_customer_algorithm: SSECustomerAlgorithm | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerAlgorithm',
        serialization_name='x-amz-server-side-encryption-customer-algorithm',
        shape_name='SSECustomerAlgorithm',
    ))

    sse_customer_key: SSECustomerKey | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerKey',
        serialization_name='x-amz-server-side-encryption-customer-key',
        shape_name='SSECustomerKey',
    ))

    sse_customer_key_md5: SSECustomerKeyMD5 | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSECustomerKeyMD5',
        serialization_name='x-amz-server-side-encryption-customer-key-MD5',
        shape_name='SSECustomerKeyMD5',
    ))

    sse_kms_key_id: SSEKMSKeyId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSEKMSKeyId',
        serialization_name='x-amz-server-side-encryption-aws-kms-key-id',
        shape_name='SSEKMSKeyId',
    ))

    sse_kms_encryption_context: SSEKMSEncryptionContext | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SSEKMSEncryptionContext',
        serialization_name='x-amz-server-side-encryption-context',
        shape_name='SSEKMSEncryptionContext',
    ))

    bucket_key_enabled: BucketKeyEnabled | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BucketKeyEnabled',
        serialization_name='x-amz-server-side-encryption-bucket-key-enabled',
        shape_name='BucketKeyEnabled',
    ))

    request_payer: RequestPayer | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequestPayer',
        serialization_name='x-amz-request-payer',
        shape_name='RequestPayer',
    ))

    tagging: TaggingHeader | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tagging',
        serialization_name='x-amz-tagging',
        shape_name='TaggingHeader',
    ))

    object_lock_mode: ObjectLockMode | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ObjectLockMode',
        serialization_name='x-amz-object-lock-mode',
        shape_name='ObjectLockMode',
    ))

    object_lock_retain_until_date: ObjectLockRetainUntilDate | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ObjectLockRetainUntilDate',
        serialization_name='x-amz-object-lock-retain-until-date',
        shape_name='ObjectLockRetainUntilDate',
    ))

    object_lock_legal_hold_status: ObjectLockLegalHoldStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ObjectLockLegalHoldStatus',
        serialization_name='x-amz-object-lock-legal-hold',
        shape_name='ObjectLockLegalHoldStatus',
    ))

    expected_bucket_owner: AccountId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ExpectedBucketOwner',
        serialization_name='x-amz-expected-bucket-owner',
        shape_name='AccountId',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ListBucketsOutput(
    _base.Shape,
    shape_name='ListBucketsOutput',
):
    buckets: Buckets | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Buckets',
        value_type=_base.ListValueType(Bucket),
        shape_name='Buckets',
    ))

    owner: Owner | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Owner',
        shape_name='Owner',
    ))

    continuation_token: NextToken | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContinuationToken',
        shape_name='NextToken',
    ))

    prefix: Prefix | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Prefix',
        shape_name='Prefix',
    ))


ObjectList: _ta.TypeAlias = _ta.Sequence[Object]


@_dc.dataclass(frozen=True, kw_only=True)
class ListObjectsV2Output(
    _base.Shape,
    shape_name='ListObjectsV2Output',
):
    is_truncated: IsTruncated | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IsTruncated',
        shape_name='IsTruncated',
    ))

    contents: ObjectList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Contents',
        value_type=_base.ListValueType(Object),
        shape_name='ObjectList',
    ))

    name: BucketName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        shape_name='BucketName',
    ))

    prefix: Prefix | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Prefix',
        shape_name='Prefix',
    ))

    delimiter: Delimiter | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Delimiter',
        shape_name='Delimiter',
    ))

    max_keys: MaxKeys | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxKeys',
        shape_name='MaxKeys',
    ))

    common_prefixes: CommonPrefixList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CommonPrefixes',
        value_type=_base.ListValueType(CommonPrefix),
        shape_name='CommonPrefixList',
    ))

    encoding_type: EncodingType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EncodingType',
        shape_name='EncodingType',
    ))

    key_count: KeyCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyCount',
        shape_name='KeyCount',
    ))

    continuation_token: Token | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ContinuationToken',
        shape_name='Token',
    ))

    next_continuation_token: NextToken | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextContinuationToken',
        shape_name='NextToken',
    ))

    start_after: StartAfter | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StartAfter',
        shape_name='StartAfter',
    ))

    request_charged: RequestCharged | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequestCharged',
        serialization_name='x-amz-request-charged',
        shape_name='RequestCharged',
    ))


ALL_SHAPES: frozenset[type[_base.Shape]] = frozenset([
    Bucket,
    CommonPrefix,
    DeleteObjectOutput,
    DeleteObjectRequest,
    EncryptionTypeMismatch,
    GetObjectOutput,
    GetObjectRequest,
    InvalidObjectState,
    InvalidRequest,
    InvalidWriteOffset,
    ListBucketsOutput,
    ListBucketsRequest,
    ListObjectsV2Output,
    ListObjectsV2Request,
    NoSuchBucket,
    NoSuchKey,
    Object,
    Owner,
    PutObjectOutput,
    PutObjectRequest,
    RestoreStatus,
    TooManyParts,
])


##


DELETE_OBJECT = _base.Operation(
    name='DeleteObject',
    input=DeleteObjectRequest,
    output=DeleteObjectOutput,
)

GET_OBJECT = _base.Operation(
    name='GetObject',
    input=GetObjectRequest,
    output=GetObjectOutput,
    errors=[
        InvalidObjectState,
        NoSuchKey,
    ],
)

LIST_BUCKETS = _base.Operation(
    name='ListBuckets',
    input=ListBucketsRequest,
    output=ListBucketsOutput,
)

LIST_OBJECTS_V2 = _base.Operation(
    name='ListObjectsV2',
    input=ListObjectsV2Request,
    output=ListObjectsV2Output,
    errors=[
        NoSuchBucket,
    ],
)

PUT_OBJECT = _base.Operation(
    name='PutObject',
    input=PutObjectRequest,
    output=PutObjectOutput,
    errors=[
        EncryptionTypeMismatch,
        InvalidRequest,
        InvalidWriteOffset,
        TooManyParts,
    ],
)


ALL_OPERATIONS: frozenset[_base.Operation] = frozenset([
    DELETE_OBJECT,
    GET_OBJECT,
    LIST_BUCKETS,
    LIST_OBJECTS_V2,
    PUT_OBJECT,
])
