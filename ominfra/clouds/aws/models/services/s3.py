# flake8: noqa: E501
# ruff: noqa: N801 S105
# fmt: off
import dataclasses as _dc  # noqa
import enum as _enum  # noqa
import typing as _ta  # noqa

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


ChecksumCRC32 = _ta.NewType('ChecksumCRC32', str)

ChecksumCRC32C = _ta.NewType('ChecksumCRC32C', str)


class ChecksumMode(_enum.Enum):
    ENABLED = 'ENABLED'


ChecksumSHA1 = _ta.NewType('ChecksumSHA1', str)

ChecksumSHA256 = _ta.NewType('ChecksumSHA256', str)

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


@_dc.dataclass(frozen=True)
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


@_dc.dataclass(frozen=True)
class InvalidRequest(
    _base.Shape,
    shape_name='InvalidRequest',
):
    pass


@_dc.dataclass(frozen=True)
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


@_dc.dataclass(frozen=True)
class NoSuchBucket(
    _base.Shape,
    shape_name='NoSuchBucket',
):
    pass


@_dc.dataclass(frozen=True)
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

SSECustomerAlgorithm = _ta.NewType('SSECustomerAlgorithm', str)

SSECustomerKey = _ta.NewType('SSECustomerKey', str)

SSECustomerKeyMD5 = _ta.NewType('SSECustomerKeyMD5', str)

SSEKMSEncryptionContext = _ta.NewType('SSEKMSEncryptionContext', str)

SSEKMSKeyId = _ta.NewType('SSEKMSKeyId', str)


class ServerSideEncryption(_enum.Enum):
    AES256 = 'AES256'
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


TagCount = _ta.NewType('TagCount', int)

TaggingHeader = _ta.NewType('TaggingHeader', str)

Token = _ta.NewType('Token', str)


@_dc.dataclass(frozen=True)
class TooManyParts(
    _base.Shape,
    shape_name='TooManyParts',
):
    pass


WebsiteRedirectLocation = _ta.NewType('WebsiteRedirectLocation', str)

WriteOffsetBytes = _ta.NewType('WriteOffsetBytes', int)


@_dc.dataclass(frozen=True)
class Bucket(
    _base.Shape,
    shape_name='Bucket',
):
    name: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='BucketName',
    ))

    creation_date: CreationDate = _dc.field(metadata=_base.field_metadata(
        member_name='CreationDate',
        shape_name='CreationDate',
    ))

    bucket_region: BucketRegion = _dc.field(metadata=_base.field_metadata(
        member_name='BucketRegion',
        shape_name='BucketRegion',
    ))


ChecksumAlgorithmList: _ta.TypeAlias = _ta.Sequence[ChecksumAlgorithm]


@_dc.dataclass(frozen=True)
class CommonPrefix(
    _base.Shape,
    shape_name='CommonPrefix',
):
    prefix: Prefix = _dc.field(metadata=_base.field_metadata(
        member_name='Prefix',
        shape_name='Prefix',
    ))


@_dc.dataclass(frozen=True)
class DeleteObjectOutput(
    _base.Shape,
    shape_name='DeleteObjectOutput',
):
    delete_marker: DeleteMarker = _dc.field(metadata=_base.field_metadata(
        member_name='DeleteMarker',
        shape_name='DeleteMarker',
    ))

    version_id: ObjectVersionId = _dc.field(metadata=_base.field_metadata(
        member_name='VersionId',
        shape_name='ObjectVersionId',
    ))

    request_charged: RequestCharged = _dc.field(metadata=_base.field_metadata(
        member_name='RequestCharged',
        shape_name='RequestCharged',
    ))


@_dc.dataclass(frozen=True)
class DeleteObjectRequest(
    _base.Shape,
    shape_name='DeleteObjectRequest',
):
    bucket: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Bucket',
        shape_name='BucketName',
    ))

    key: ObjectKey = _dc.field(metadata=_base.field_metadata(
        member_name='Key',
        shape_name='ObjectKey',
    ))

    mfa: MFA = _dc.field(metadata=_base.field_metadata(
        member_name='MFA',
        shape_name='MFA',
    ))

    version_id: ObjectVersionId = _dc.field(metadata=_base.field_metadata(
        member_name='VersionId',
        shape_name='ObjectVersionId',
    ))

    request_payer: RequestPayer = _dc.field(metadata=_base.field_metadata(
        member_name='RequestPayer',
        shape_name='RequestPayer',
    ))

    bypass_governance_retention: BypassGovernanceRetention = _dc.field(metadata=_base.field_metadata(
        member_name='BypassGovernanceRetention',
        shape_name='BypassGovernanceRetention',
    ))

    expected_bucket_owner: AccountId = _dc.field(metadata=_base.field_metadata(
        member_name='ExpectedBucketOwner',
        shape_name='AccountId',
    ))

    if_match: IfMatch = _dc.field(metadata=_base.field_metadata(
        member_name='IfMatch',
        shape_name='IfMatch',
    ))

    if_match_last_modified_time: IfMatchLastModifiedTime = _dc.field(metadata=_base.field_metadata(
        member_name='IfMatchLastModifiedTime',
        shape_name='IfMatchLastModifiedTime',
    ))

    if_match_size: IfMatchSize = _dc.field(metadata=_base.field_metadata(
        member_name='IfMatchSize',
        shape_name='IfMatchSize',
    ))


@_dc.dataclass(frozen=True)
class GetObjectRequest(
    _base.Shape,
    shape_name='GetObjectRequest',
):
    bucket: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Bucket',
        shape_name='BucketName',
    ))

    if_match: IfMatch = _dc.field(metadata=_base.field_metadata(
        member_name='IfMatch',
        shape_name='IfMatch',
    ))

    if_modified_since: IfModifiedSince = _dc.field(metadata=_base.field_metadata(
        member_name='IfModifiedSince',
        shape_name='IfModifiedSince',
    ))

    if_none_match: IfNoneMatch = _dc.field(metadata=_base.field_metadata(
        member_name='IfNoneMatch',
        shape_name='IfNoneMatch',
    ))

    if_unmodified_since: IfUnmodifiedSince = _dc.field(metadata=_base.field_metadata(
        member_name='IfUnmodifiedSince',
        shape_name='IfUnmodifiedSince',
    ))

    key: ObjectKey = _dc.field(metadata=_base.field_metadata(
        member_name='Key',
        shape_name='ObjectKey',
    ))

    range: Range = _dc.field(metadata=_base.field_metadata(
        member_name='Range',
        shape_name='Range',
    ))

    response_cache_control: ResponseCacheControl = _dc.field(metadata=_base.field_metadata(
        member_name='ResponseCacheControl',
        shape_name='ResponseCacheControl',
    ))

    response_content_disposition: ResponseContentDisposition = _dc.field(metadata=_base.field_metadata(
        member_name='ResponseContentDisposition',
        shape_name='ResponseContentDisposition',
    ))

    response_content_encoding: ResponseContentEncoding = _dc.field(metadata=_base.field_metadata(
        member_name='ResponseContentEncoding',
        shape_name='ResponseContentEncoding',
    ))

    response_content_language: ResponseContentLanguage = _dc.field(metadata=_base.field_metadata(
        member_name='ResponseContentLanguage',
        shape_name='ResponseContentLanguage',
    ))

    response_content_type: ResponseContentType = _dc.field(metadata=_base.field_metadata(
        member_name='ResponseContentType',
        shape_name='ResponseContentType',
    ))

    response_expires: ResponseExpires = _dc.field(metadata=_base.field_metadata(
        member_name='ResponseExpires',
        shape_name='ResponseExpires',
    ))

    version_id: ObjectVersionId = _dc.field(metadata=_base.field_metadata(
        member_name='VersionId',
        shape_name='ObjectVersionId',
    ))

    sse_customer_algorithm: SSECustomerAlgorithm = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerAlgorithm',
        shape_name='SSECustomerAlgorithm',
    ))

    sse_customer_key: SSECustomerKey = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerKey',
        shape_name='SSECustomerKey',
    ))

    sse_customer_key_md5: SSECustomerKeyMD5 = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerKeyMD5',
        shape_name='SSECustomerKeyMD5',
    ))

    request_payer: RequestPayer = _dc.field(metadata=_base.field_metadata(
        member_name='RequestPayer',
        shape_name='RequestPayer',
    ))

    part_number: PartNumber = _dc.field(metadata=_base.field_metadata(
        member_name='PartNumber',
        shape_name='PartNumber',
    ))

    expected_bucket_owner: AccountId = _dc.field(metadata=_base.field_metadata(
        member_name='ExpectedBucketOwner',
        shape_name='AccountId',
    ))

    checksum_mode: ChecksumMode = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumMode',
        shape_name='ChecksumMode',
    ))


@_dc.dataclass(frozen=True)
class InvalidObjectState(
    _base.Shape,
    shape_name='InvalidObjectState',
):
    storage_class: StorageClass = _dc.field(metadata=_base.field_metadata(
        member_name='StorageClass',
        shape_name='StorageClass',
    ))

    access_tier: IntelligentTieringAccessTier = _dc.field(metadata=_base.field_metadata(
        member_name='AccessTier',
        shape_name='IntelligentTieringAccessTier',
    ))


@_dc.dataclass(frozen=True)
class ListBucketsRequest(
    _base.Shape,
    shape_name='ListBucketsRequest',
):
    max_buckets: MaxBuckets = _dc.field(metadata=_base.field_metadata(
        member_name='MaxBuckets',
        shape_name='MaxBuckets',
    ))

    continuation_token: Token = _dc.field(metadata=_base.field_metadata(
        member_name='ContinuationToken',
        shape_name='Token',
    ))

    prefix: Prefix = _dc.field(metadata=_base.field_metadata(
        member_name='Prefix',
        shape_name='Prefix',
    ))

    bucket_region: BucketRegion = _dc.field(metadata=_base.field_metadata(
        member_name='BucketRegion',
        shape_name='BucketRegion',
    ))


Metadata: _ta.TypeAlias = _ta.Mapping[MetadataKey, MetadataKey]

OptionalObjectAttributesList: _ta.TypeAlias = _ta.Sequence[OptionalObjectAttributes]


@_dc.dataclass(frozen=True)
class Owner(
    _base.Shape,
    shape_name='Owner',
):
    display_name: DisplayName = _dc.field(metadata=_base.field_metadata(
        member_name='DisplayName',
        shape_name='DisplayName',
    ))

    i_d: ID = _dc.field(metadata=_base.field_metadata(
        member_name='ID',
        shape_name='ID',
    ))


@_dc.dataclass(frozen=True)
class PutObjectOutput(
    _base.Shape,
    shape_name='PutObjectOutput',
):
    expiration: Expiration = _dc.field(metadata=_base.field_metadata(
        member_name='Expiration',
        shape_name='Expiration',
    ))

    etag: ETag = _dc.field(metadata=_base.field_metadata(
        member_name='ETag',
        shape_name='ETag',
    ))

    checksum_crc32: ChecksumCRC32 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumCRC32',
        shape_name='ChecksumCRC32',
    ))

    checksum_crc32c: ChecksumCRC32C = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumCRC32C',
        shape_name='ChecksumCRC32C',
    ))

    checksum_sha1: ChecksumSHA1 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumSHA1',
        shape_name='ChecksumSHA1',
    ))

    checksum_sha256: ChecksumSHA256 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumSHA256',
        shape_name='ChecksumSHA256',
    ))

    server_side_encryption: ServerSideEncryption = _dc.field(metadata=_base.field_metadata(
        member_name='ServerSideEncryption',
        shape_name='ServerSideEncryption',
    ))

    version_id: ObjectVersionId = _dc.field(metadata=_base.field_metadata(
        member_name='VersionId',
        shape_name='ObjectVersionId',
    ))

    sse_customer_algorithm: SSECustomerAlgorithm = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerAlgorithm',
        shape_name='SSECustomerAlgorithm',
    ))

    sse_customer_key_md5: SSECustomerKeyMD5 = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerKeyMD5',
        shape_name='SSECustomerKeyMD5',
    ))

    sse_kms_key_id: SSEKMSKeyId = _dc.field(metadata=_base.field_metadata(
        member_name='SSEKMSKeyId',
        shape_name='SSEKMSKeyId',
    ))

    sse_kms_encryption_context: SSEKMSEncryptionContext = _dc.field(metadata=_base.field_metadata(
        member_name='SSEKMSEncryptionContext',
        shape_name='SSEKMSEncryptionContext',
    ))

    bucket_key_enabled: BucketKeyEnabled = _dc.field(metadata=_base.field_metadata(
        member_name='BucketKeyEnabled',
        shape_name='BucketKeyEnabled',
    ))

    size: Size = _dc.field(metadata=_base.field_metadata(
        member_name='Size',
        shape_name='Size',
    ))

    request_charged: RequestCharged = _dc.field(metadata=_base.field_metadata(
        member_name='RequestCharged',
        shape_name='RequestCharged',
    ))


@_dc.dataclass(frozen=True)
class RestoreStatus(
    _base.Shape,
    shape_name='RestoreStatus',
):
    is_restore_in_progress: IsRestoreInProgress = _dc.field(metadata=_base.field_metadata(
        member_name='IsRestoreInProgress',
        shape_name='IsRestoreInProgress',
    ))

    restore_expiry_date: RestoreExpiryDate = _dc.field(metadata=_base.field_metadata(
        member_name='RestoreExpiryDate',
        shape_name='RestoreExpiryDate',
    ))


Buckets: _ta.TypeAlias = _ta.Sequence[Bucket]

CommonPrefixList: _ta.TypeAlias = _ta.Sequence[CommonPrefix]


@_dc.dataclass(frozen=True)
class GetObjectOutput(
    _base.Shape,
    shape_name='GetObjectOutput',
):
    body: Body = _dc.field(metadata=_base.field_metadata(
        member_name='Body',
        shape_name='Body',
    ))

    delete_marker: DeleteMarker = _dc.field(metadata=_base.field_metadata(
        member_name='DeleteMarker',
        shape_name='DeleteMarker',
    ))

    accept_ranges: AcceptRanges = _dc.field(metadata=_base.field_metadata(
        member_name='AcceptRanges',
        shape_name='AcceptRanges',
    ))

    expiration: Expiration = _dc.field(metadata=_base.field_metadata(
        member_name='Expiration',
        shape_name='Expiration',
    ))

    restore: Restore = _dc.field(metadata=_base.field_metadata(
        member_name='Restore',
        shape_name='Restore',
    ))

    last_modified: LastModified = _dc.field(metadata=_base.field_metadata(
        member_name='LastModified',
        shape_name='LastModified',
    ))

    content_length: ContentLength = _dc.field(metadata=_base.field_metadata(
        member_name='ContentLength',
        shape_name='ContentLength',
    ))

    etag: ETag = _dc.field(metadata=_base.field_metadata(
        member_name='ETag',
        shape_name='ETag',
    ))

    checksum_crc32: ChecksumCRC32 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumCRC32',
        shape_name='ChecksumCRC32',
    ))

    checksum_crc32c: ChecksumCRC32C = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumCRC32C',
        shape_name='ChecksumCRC32C',
    ))

    checksum_sha1: ChecksumSHA1 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumSHA1',
        shape_name='ChecksumSHA1',
    ))

    checksum_sha256: ChecksumSHA256 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumSHA256',
        shape_name='ChecksumSHA256',
    ))

    missing_meta: MissingMeta = _dc.field(metadata=_base.field_metadata(
        member_name='MissingMeta',
        shape_name='MissingMeta',
    ))

    version_id: ObjectVersionId = _dc.field(metadata=_base.field_metadata(
        member_name='VersionId',
        shape_name='ObjectVersionId',
    ))

    cache_control: CacheControl = _dc.field(metadata=_base.field_metadata(
        member_name='CacheControl',
        shape_name='CacheControl',
    ))

    content_disposition: ContentDisposition = _dc.field(metadata=_base.field_metadata(
        member_name='ContentDisposition',
        shape_name='ContentDisposition',
    ))

    content_encoding: ContentEncoding = _dc.field(metadata=_base.field_metadata(
        member_name='ContentEncoding',
        shape_name='ContentEncoding',
    ))

    content_language: ContentLanguage = _dc.field(metadata=_base.field_metadata(
        member_name='ContentLanguage',
        shape_name='ContentLanguage',
    ))

    content_range: ContentRange = _dc.field(metadata=_base.field_metadata(
        member_name='ContentRange',
        shape_name='ContentRange',
    ))

    content_type: ContentType = _dc.field(metadata=_base.field_metadata(
        member_name='ContentType',
        shape_name='ContentType',
    ))

    expires: Expires = _dc.field(metadata=_base.field_metadata(
        member_name='Expires',
        shape_name='Expires',
    ))

    website_redirect_location: WebsiteRedirectLocation = _dc.field(metadata=_base.field_metadata(
        member_name='WebsiteRedirectLocation',
        shape_name='WebsiteRedirectLocation',
    ))

    server_side_encryption: ServerSideEncryption = _dc.field(metadata=_base.field_metadata(
        member_name='ServerSideEncryption',
        shape_name='ServerSideEncryption',
    ))

    metadata: Metadata = _dc.field(metadata=_base.field_metadata(
        member_name='Metadata',
        shape_name='Metadata',
    ))

    sse_customer_algorithm: SSECustomerAlgorithm = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerAlgorithm',
        shape_name='SSECustomerAlgorithm',
    ))

    sse_customer_key_md5: SSECustomerKeyMD5 = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerKeyMD5',
        shape_name='SSECustomerKeyMD5',
    ))

    sse_kms_key_id: SSEKMSKeyId = _dc.field(metadata=_base.field_metadata(
        member_name='SSEKMSKeyId',
        shape_name='SSEKMSKeyId',
    ))

    bucket_key_enabled: BucketKeyEnabled = _dc.field(metadata=_base.field_metadata(
        member_name='BucketKeyEnabled',
        shape_name='BucketKeyEnabled',
    ))

    storage_class: StorageClass = _dc.field(metadata=_base.field_metadata(
        member_name='StorageClass',
        shape_name='StorageClass',
    ))

    request_charged: RequestCharged = _dc.field(metadata=_base.field_metadata(
        member_name='RequestCharged',
        shape_name='RequestCharged',
    ))

    replication_status: ReplicationStatus = _dc.field(metadata=_base.field_metadata(
        member_name='ReplicationStatus',
        shape_name='ReplicationStatus',
    ))

    parts_count: PartsCount = _dc.field(metadata=_base.field_metadata(
        member_name='PartsCount',
        shape_name='PartsCount',
    ))

    tag_count: TagCount = _dc.field(metadata=_base.field_metadata(
        member_name='TagCount',
        shape_name='TagCount',
    ))

    object_lock_mode: ObjectLockMode = _dc.field(metadata=_base.field_metadata(
        member_name='ObjectLockMode',
        shape_name='ObjectLockMode',
    ))

    object_lock_retain_until_date: ObjectLockRetainUntilDate = _dc.field(metadata=_base.field_metadata(
        member_name='ObjectLockRetainUntilDate',
        shape_name='ObjectLockRetainUntilDate',
    ))

    object_lock_legal_hold_status: ObjectLockLegalHoldStatus = _dc.field(metadata=_base.field_metadata(
        member_name='ObjectLockLegalHoldStatus',
        shape_name='ObjectLockLegalHoldStatus',
    ))


@_dc.dataclass(frozen=True)
class ListObjectsV2Request(
    _base.Shape,
    shape_name='ListObjectsV2Request',
):
    bucket: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Bucket',
        shape_name='BucketName',
    ))

    delimiter: Delimiter = _dc.field(metadata=_base.field_metadata(
        member_name='Delimiter',
        shape_name='Delimiter',
    ))

    encoding_type: EncodingType = _dc.field(metadata=_base.field_metadata(
        member_name='EncodingType',
        shape_name='EncodingType',
    ))

    max_keys: MaxKeys = _dc.field(metadata=_base.field_metadata(
        member_name='MaxKeys',
        shape_name='MaxKeys',
    ))

    prefix: Prefix = _dc.field(metadata=_base.field_metadata(
        member_name='Prefix',
        shape_name='Prefix',
    ))

    continuation_token: Token = _dc.field(metadata=_base.field_metadata(
        member_name='ContinuationToken',
        shape_name='Token',
    ))

    fetch_owner: FetchOwner = _dc.field(metadata=_base.field_metadata(
        member_name='FetchOwner',
        shape_name='FetchOwner',
    ))

    start_after: StartAfter = _dc.field(metadata=_base.field_metadata(
        member_name='StartAfter',
        shape_name='StartAfter',
    ))

    request_payer: RequestPayer = _dc.field(metadata=_base.field_metadata(
        member_name='RequestPayer',
        shape_name='RequestPayer',
    ))

    expected_bucket_owner: AccountId = _dc.field(metadata=_base.field_metadata(
        member_name='ExpectedBucketOwner',
        shape_name='AccountId',
    ))

    optional_object_attributes: OptionalObjectAttributesList = _dc.field(metadata=_base.field_metadata(
        member_name='OptionalObjectAttributes',
        shape_name='OptionalObjectAttributesList',
    ))


@_dc.dataclass(frozen=True)
class Object(
    _base.Shape,
    shape_name='Object',
):
    key: ObjectKey = _dc.field(metadata=_base.field_metadata(
        member_name='Key',
        shape_name='ObjectKey',
    ))

    last_modified: LastModified = _dc.field(metadata=_base.field_metadata(
        member_name='LastModified',
        shape_name='LastModified',
    ))

    etag: ETag = _dc.field(metadata=_base.field_metadata(
        member_name='ETag',
        shape_name='ETag',
    ))

    checksum_algorithm: ChecksumAlgorithmList = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumAlgorithm',
        shape_name='ChecksumAlgorithmList',
    ))

    size: Size = _dc.field(metadata=_base.field_metadata(
        member_name='Size',
        shape_name='Size',
    ))

    storage_class: ObjectStorageClass = _dc.field(metadata=_base.field_metadata(
        member_name='StorageClass',
        shape_name='ObjectStorageClass',
    ))

    owner: Owner = _dc.field(metadata=_base.field_metadata(
        member_name='Owner',
        shape_name='Owner',
    ))

    restore_status: RestoreStatus = _dc.field(metadata=_base.field_metadata(
        member_name='RestoreStatus',
        shape_name='RestoreStatus',
    ))


@_dc.dataclass(frozen=True)
class PutObjectRequest(
    _base.Shape,
    shape_name='PutObjectRequest',
):
    acl: ObjectCannedACL = _dc.field(metadata=_base.field_metadata(
        member_name='ACL',
        shape_name='ObjectCannedACL',
    ))

    body: Body = _dc.field(metadata=_base.field_metadata(
        member_name='Body',
        shape_name='Body',
    ))

    bucket: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Bucket',
        shape_name='BucketName',
    ))

    cache_control: CacheControl = _dc.field(metadata=_base.field_metadata(
        member_name='CacheControl',
        shape_name='CacheControl',
    ))

    content_disposition: ContentDisposition = _dc.field(metadata=_base.field_metadata(
        member_name='ContentDisposition',
        shape_name='ContentDisposition',
    ))

    content_encoding: ContentEncoding = _dc.field(metadata=_base.field_metadata(
        member_name='ContentEncoding',
        shape_name='ContentEncoding',
    ))

    content_language: ContentLanguage = _dc.field(metadata=_base.field_metadata(
        member_name='ContentLanguage',
        shape_name='ContentLanguage',
    ))

    content_length: ContentLength = _dc.field(metadata=_base.field_metadata(
        member_name='ContentLength',
        shape_name='ContentLength',
    ))

    content_md5: ContentMD5 = _dc.field(metadata=_base.field_metadata(
        member_name='ContentMD5',
        shape_name='ContentMD5',
    ))

    content_type: ContentType = _dc.field(metadata=_base.field_metadata(
        member_name='ContentType',
        shape_name='ContentType',
    ))

    checksum_algorithm: ChecksumAlgorithm = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumAlgorithm',
        shape_name='ChecksumAlgorithm',
    ))

    checksum_crc32: ChecksumCRC32 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumCRC32',
        shape_name='ChecksumCRC32',
    ))

    checksum_crc32c: ChecksumCRC32C = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumCRC32C',
        shape_name='ChecksumCRC32C',
    ))

    checksum_sha1: ChecksumSHA1 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumSHA1',
        shape_name='ChecksumSHA1',
    ))

    checksum_sha256: ChecksumSHA256 = _dc.field(metadata=_base.field_metadata(
        member_name='ChecksumSHA256',
        shape_name='ChecksumSHA256',
    ))

    expires: Expires = _dc.field(metadata=_base.field_metadata(
        member_name='Expires',
        shape_name='Expires',
    ))

    if_match: IfMatch = _dc.field(metadata=_base.field_metadata(
        member_name='IfMatch',
        shape_name='IfMatch',
    ))

    if_none_match: IfNoneMatch = _dc.field(metadata=_base.field_metadata(
        member_name='IfNoneMatch',
        shape_name='IfNoneMatch',
    ))

    grant_full_control: GrantFullControl = _dc.field(metadata=_base.field_metadata(
        member_name='GrantFullControl',
        shape_name='GrantFullControl',
    ))

    grant_read: GrantRead = _dc.field(metadata=_base.field_metadata(
        member_name='GrantRead',
        shape_name='GrantRead',
    ))

    grant_read_acp: GrantReadACP = _dc.field(metadata=_base.field_metadata(
        member_name='GrantReadACP',
        shape_name='GrantReadACP',
    ))

    grant_write_acp: GrantWriteACP = _dc.field(metadata=_base.field_metadata(
        member_name='GrantWriteACP',
        shape_name='GrantWriteACP',
    ))

    key: ObjectKey = _dc.field(metadata=_base.field_metadata(
        member_name='Key',
        shape_name='ObjectKey',
    ))

    write_offset_bytes: WriteOffsetBytes = _dc.field(metadata=_base.field_metadata(
        member_name='WriteOffsetBytes',
        shape_name='WriteOffsetBytes',
    ))

    metadata: Metadata = _dc.field(metadata=_base.field_metadata(
        member_name='Metadata',
        shape_name='Metadata',
    ))

    server_side_encryption: ServerSideEncryption = _dc.field(metadata=_base.field_metadata(
        member_name='ServerSideEncryption',
        shape_name='ServerSideEncryption',
    ))

    storage_class: StorageClass = _dc.field(metadata=_base.field_metadata(
        member_name='StorageClass',
        shape_name='StorageClass',
    ))

    website_redirect_location: WebsiteRedirectLocation = _dc.field(metadata=_base.field_metadata(
        member_name='WebsiteRedirectLocation',
        shape_name='WebsiteRedirectLocation',
    ))

    sse_customer_algorithm: SSECustomerAlgorithm = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerAlgorithm',
        shape_name='SSECustomerAlgorithm',
    ))

    sse_customer_key: SSECustomerKey = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerKey',
        shape_name='SSECustomerKey',
    ))

    sse_customer_key_md5: SSECustomerKeyMD5 = _dc.field(metadata=_base.field_metadata(
        member_name='SSECustomerKeyMD5',
        shape_name='SSECustomerKeyMD5',
    ))

    sse_kms_key_id: SSEKMSKeyId = _dc.field(metadata=_base.field_metadata(
        member_name='SSEKMSKeyId',
        shape_name='SSEKMSKeyId',
    ))

    sse_kms_encryption_context: SSEKMSEncryptionContext = _dc.field(metadata=_base.field_metadata(
        member_name='SSEKMSEncryptionContext',
        shape_name='SSEKMSEncryptionContext',
    ))

    bucket_key_enabled: BucketKeyEnabled = _dc.field(metadata=_base.field_metadata(
        member_name='BucketKeyEnabled',
        shape_name='BucketKeyEnabled',
    ))

    request_payer: RequestPayer = _dc.field(metadata=_base.field_metadata(
        member_name='RequestPayer',
        shape_name='RequestPayer',
    ))

    tagging: TaggingHeader = _dc.field(metadata=_base.field_metadata(
        member_name='Tagging',
        shape_name='TaggingHeader',
    ))

    object_lock_mode: ObjectLockMode = _dc.field(metadata=_base.field_metadata(
        member_name='ObjectLockMode',
        shape_name='ObjectLockMode',
    ))

    object_lock_retain_until_date: ObjectLockRetainUntilDate = _dc.field(metadata=_base.field_metadata(
        member_name='ObjectLockRetainUntilDate',
        shape_name='ObjectLockRetainUntilDate',
    ))

    object_lock_legal_hold_status: ObjectLockLegalHoldStatus = _dc.field(metadata=_base.field_metadata(
        member_name='ObjectLockLegalHoldStatus',
        shape_name='ObjectLockLegalHoldStatus',
    ))

    expected_bucket_owner: AccountId = _dc.field(metadata=_base.field_metadata(
        member_name='ExpectedBucketOwner',
        shape_name='AccountId',
    ))


@_dc.dataclass(frozen=True)
class ListBucketsOutput(
    _base.Shape,
    shape_name='ListBucketsOutput',
):
    buckets: Buckets = _dc.field(metadata=_base.field_metadata(
        member_name='Buckets',
        shape_name='Buckets',
    ))

    owner: Owner = _dc.field(metadata=_base.field_metadata(
        member_name='Owner',
        shape_name='Owner',
    ))

    continuation_token: NextToken = _dc.field(metadata=_base.field_metadata(
        member_name='ContinuationToken',
        shape_name='NextToken',
    ))

    prefix: Prefix = _dc.field(metadata=_base.field_metadata(
        member_name='Prefix',
        shape_name='Prefix',
    ))


ObjectList: _ta.TypeAlias = _ta.Sequence[Object]


@_dc.dataclass(frozen=True)
class ListObjectsV2Output(
    _base.Shape,
    shape_name='ListObjectsV2Output',
):
    is_truncated: IsTruncated = _dc.field(metadata=_base.field_metadata(
        member_name='IsTruncated',
        shape_name='IsTruncated',
    ))

    contents: ObjectList = _dc.field(metadata=_base.field_metadata(
        member_name='Contents',
        shape_name='ObjectList',
    ))

    name: BucketName = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='BucketName',
    ))

    prefix: Prefix = _dc.field(metadata=_base.field_metadata(
        member_name='Prefix',
        shape_name='Prefix',
    ))

    delimiter: Delimiter = _dc.field(metadata=_base.field_metadata(
        member_name='Delimiter',
        shape_name='Delimiter',
    ))

    max_keys: MaxKeys = _dc.field(metadata=_base.field_metadata(
        member_name='MaxKeys',
        shape_name='MaxKeys',
    ))

    common_prefixes: CommonPrefixList = _dc.field(metadata=_base.field_metadata(
        member_name='CommonPrefixes',
        shape_name='CommonPrefixList',
    ))

    encoding_type: EncodingType = _dc.field(metadata=_base.field_metadata(
        member_name='EncodingType',
        shape_name='EncodingType',
    ))

    key_count: KeyCount = _dc.field(metadata=_base.field_metadata(
        member_name='KeyCount',
        shape_name='KeyCount',
    ))

    continuation_token: Token = _dc.field(metadata=_base.field_metadata(
        member_name='ContinuationToken',
        shape_name='Token',
    ))

    next_continuation_token: NextToken = _dc.field(metadata=_base.field_metadata(
        member_name='NextContinuationToken',
        shape_name='NextToken',
    ))

    start_after: StartAfter = _dc.field(metadata=_base.field_metadata(
        member_name='StartAfter',
        shape_name='StartAfter',
    ))

    request_charged: RequestCharged = _dc.field(metadata=_base.field_metadata(
        member_name='RequestCharged',
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
