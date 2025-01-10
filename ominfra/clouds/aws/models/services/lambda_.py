# flake8: noqa: E501
# ruff: noqa: N801 S105
# fmt: off
import dataclasses as _dc  # noqa
import enum as _enum  # noqa
import typing as _ta  # noqa

from .. import base as _base  # noqa


##


class ApplicationLogLevel(_enum.Enum):
    TRACE = 'TRACE'
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'
    FATAL = 'FATAL'


class Architecture(_enum.Enum):
    X86_64 = 'x86_64'
    ARM64 = 'arm64'


Arn = _ta.NewType('Arn', str)

Description = _ta.NewType('Description', str)

EnvironmentVariableName = _ta.NewType('EnvironmentVariableName', str)

EnvironmentVariableValue = _ta.NewType('EnvironmentVariableValue', str)

EphemeralStorageSize = _ta.NewType('EphemeralStorageSize', int)

FileSystemArn = _ta.NewType('FileSystemArn', str)

FunctionArn = _ta.NewType('FunctionArn', str)


class FunctionVersion(_enum.Enum):
    ALL = 'ALL'


Handler = _ta.NewType('Handler', str)

KMSKeyArn = _ta.NewType('KMSKeyArn', str)


class LastUpdateStatus(_enum.Enum):
    SUCCESSFUL = 'Successful'
    FAILED = 'Failed'
    IN_PROGRESS = 'InProgress'


LastUpdateStatusReason = _ta.NewType('LastUpdateStatusReason', str)


class LastUpdateStatusReasonCode(_enum.Enum):
    ENI_LIMIT_EXCEEDED = 'EniLimitExceeded'
    INSUFFICIENT_ROLE_PERMISSIONS = 'InsufficientRolePermissions'
    INVALID_CONFIGURATION = 'InvalidConfiguration'
    INTERNAL_ERROR = 'InternalError'
    SUBNET_OUT_OF_IP_ADDRESSES = 'SubnetOutOfIPAddresses'
    INVALID_SUBNET = 'InvalidSubnet'
    INVALID_SECURITY_GROUP = 'InvalidSecurityGroup'
    IMAGE_DELETED = 'ImageDeleted'
    IMAGE_ACCESS_DENIED = 'ImageAccessDenied'
    INVALID_IMAGE = 'InvalidImage'
    KMS_KEY_ACCESS_DENIED = 'KMSKeyAccessDenied'
    KMS_KEY_NOT_FOUND = 'KMSKeyNotFound'
    INVALID_STATE_KMS_KEY = 'InvalidStateKMSKey'
    DISABLED_KMS_KEY = 'DisabledKMSKey'
    EFS_IO_ERROR = 'EFSIOError'
    EFS_MOUNT_CONNECTIVITY_ERROR = 'EFSMountConnectivityError'
    EFS_MOUNT_FAILURE = 'EFSMountFailure'
    EFS_MOUNT_TIMEOUT = 'EFSMountTimeout'
    INVALID_RUNTIME = 'InvalidRuntime'
    INVALID_ZIP_FILE_EXCEPTION = 'InvalidZipFileException'
    FUNCTION_ERROR = 'FunctionError'


LayerVersionArn = _ta.NewType('LayerVersionArn', str)

LocalMountPath = _ta.NewType('LocalMountPath', str)


class LogFormat(_enum.Enum):
    JSON = 'JSON'
    TEXT = 'Text'


LogGroup = _ta.NewType('LogGroup', str)

Long = _ta.NewType('Long', int)

MasterRegion = _ta.NewType('MasterRegion', str)

MaxListItems = _ta.NewType('MaxListItems', int)

MemorySize = _ta.NewType('MemorySize', int)

NameSpacedFunctionArn = _ta.NewType('NameSpacedFunctionArn', str)

NamespacedFunctionName = _ta.NewType('NamespacedFunctionName', str)

NullableBoolean = _ta.NewType('NullableBoolean', bool)


class PackageType(_enum.Enum):
    ZIP = 'Zip'
    IMAGE = 'Image'


ResourceArn = _ta.NewType('ResourceArn', str)

RoleArn = _ta.NewType('RoleArn', str)


class Runtime(_enum.Enum):
    NODEJS = 'nodejs'
    NODEJS4_3 = 'nodejs4.3'
    NODEJS6_10 = 'nodejs6.10'
    NODEJS8_10 = 'nodejs8.10'
    NODEJS10_X = 'nodejs10.x'
    NODEJS12_X = 'nodejs12.x'
    NODEJS14_X = 'nodejs14.x'
    NODEJS16_X = 'nodejs16.x'
    JAVA8 = 'java8'
    JAVA8_AL2 = 'java8.al2'
    JAVA11 = 'java11'
    PYTHON2_7 = 'python2.7'
    PYTHON3_6 = 'python3.6'
    PYTHON3_7 = 'python3.7'
    PYTHON3_8 = 'python3.8'
    PYTHON3_9 = 'python3.9'
    DOTNETCORE1_0 = 'dotnetcore1.0'
    DOTNETCORE2_0 = 'dotnetcore2.0'
    DOTNETCORE2_1 = 'dotnetcore2.1'
    DOTNETCORE3_1 = 'dotnetcore3.1'
    DOTNET6 = 'dotnet6'
    DOTNET8 = 'dotnet8'
    NODEJS4_3_EDGE = 'nodejs4.3-edge'
    GO1_X = 'go1.x'
    RUBY2_5 = 'ruby2.5'
    RUBY2_7 = 'ruby2.7'
    PROVIDED = 'provided'
    PROVIDED_AL2 = 'provided.al2'
    NODEJS18_X = 'nodejs18.x'
    PYTHON3_10 = 'python3.10'
    JAVA17 = 'java17'
    RUBY3_2 = 'ruby3.2'
    RUBY3_3 = 'ruby3.3'
    PYTHON3_11 = 'python3.11'
    NODEJS20_X = 'nodejs20.x'
    PROVIDED_AL2023 = 'provided.al2023'
    PYTHON3_12 = 'python3.12'
    JAVA21 = 'java21'
    PYTHON3_13 = 'python3.13'
    NODEJS22_X = 'nodejs22.x'


RuntimeVersionArn = _ta.NewType('RuntimeVersionArn', str)

SecurityGroupId = _ta.NewType('SecurityGroupId', str)

SensitiveString = _ta.NewType('SensitiveString', str)


class SnapStartApplyOn(_enum.Enum):
    PUBLISHED_VERSIONS = 'PublishedVersions'
    NONE = 'None'


class SnapStartOptimizationStatus(_enum.Enum):
    ON = 'On'
    OFF = 'Off'


class State(_enum.Enum):
    PENDING = 'Pending'
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    FAILED = 'Failed'


StateReason = _ta.NewType('StateReason', str)


class StateReasonCode(_enum.Enum):
    IDLE = 'Idle'
    CREATING = 'Creating'
    RESTORING = 'Restoring'
    ENI_LIMIT_EXCEEDED = 'EniLimitExceeded'
    INSUFFICIENT_ROLE_PERMISSIONS = 'InsufficientRolePermissions'
    INVALID_CONFIGURATION = 'InvalidConfiguration'
    INTERNAL_ERROR = 'InternalError'
    SUBNET_OUT_OF_IP_ADDRESSES = 'SubnetOutOfIPAddresses'
    INVALID_SUBNET = 'InvalidSubnet'
    INVALID_SECURITY_GROUP = 'InvalidSecurityGroup'
    IMAGE_DELETED = 'ImageDeleted'
    IMAGE_ACCESS_DENIED = 'ImageAccessDenied'
    INVALID_IMAGE = 'InvalidImage'
    KMS_KEY_ACCESS_DENIED = 'KMSKeyAccessDenied'
    KMS_KEY_NOT_FOUND = 'KMSKeyNotFound'
    INVALID_STATE_KMS_KEY = 'InvalidStateKMSKey'
    DISABLED_KMS_KEY = 'DisabledKMSKey'
    EFS_IO_ERROR = 'EFSIOError'
    EFS_MOUNT_CONNECTIVITY_ERROR = 'EFSMountConnectivityError'
    EFS_MOUNT_FAILURE = 'EFSMountFailure'
    EFS_MOUNT_TIMEOUT = 'EFSMountTimeout'
    INVALID_RUNTIME = 'InvalidRuntime'
    INVALID_ZIP_FILE_EXCEPTION = 'InvalidZipFileException'
    FUNCTION_ERROR = 'FunctionError'


SubnetId = _ta.NewType('SubnetId', str)


class SystemLogLevel(_enum.Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'


class ThrottleReason(_enum.Enum):
    CONCURRENT_INVOCATION_LIMIT_EXCEEDED = 'ConcurrentInvocationLimitExceeded'
    FUNCTION_INVOCATION_RATE_LIMIT_EXCEEDED = 'FunctionInvocationRateLimitExceeded'
    RESERVED_FUNCTION_CONCURRENT_INVOCATION_LIMIT_EXCEEDED = 'ReservedFunctionConcurrentInvocationLimitExceeded'
    RESERVED_FUNCTION_INVOCATION_RATE_LIMIT_EXCEEDED = 'ReservedFunctionInvocationRateLimitExceeded'
    CALLER_RATE_LIMIT_EXCEEDED = 'CallerRateLimitExceeded'
    CONCURRENT_SNAPSHOT_CREATE_LIMIT_EXCEEDED = 'ConcurrentSnapshotCreateLimitExceeded'


Timeout = _ta.NewType('Timeout', int)

Timestamp = _ta.NewType('Timestamp', str)


class TracingMode(_enum.Enum):
    ACTIVE = 'Active'
    PASS_THROUGH = 'PassThrough'


Version = _ta.NewType('Version', str)

VpcId = _ta.NewType('VpcId', str)

WorkingDirectory = _ta.NewType('WorkingDirectory', str)

ArchitecturesList: _ta.TypeAlias = _ta.Sequence[Architecture]


@_dc.dataclass(frozen=True)
class DeadLetterConfig(
    _base.Shape,
    shape_name='DeadLetterConfig',
):
    target_arn: ResourceArn = _dc.field(metadata=_base.field_metadata(
        member_name='TargetArn',
        shape_name='ResourceArn',
    ))


@_dc.dataclass(frozen=True)
class EnvironmentError_(
    _base.Shape,
    shape_name='EnvironmentError',
):
    error_code: str = _dc.field(metadata=_base.field_metadata(
        member_name='ErrorCode',
        shape_name='String',
    ))

    message: SensitiveString = _dc.field(metadata=_base.field_metadata(
        member_name='Message',
        shape_name='SensitiveString',
    ))


EnvironmentVariables: _ta.TypeAlias = _ta.Mapping[EnvironmentVariableName, EnvironmentVariableName]


@_dc.dataclass(frozen=True)
class EphemeralStorage(
    _base.Shape,
    shape_name='EphemeralStorage',
):
    size: EphemeralStorageSize = _dc.field(metadata=_base.field_metadata(
        member_name='Size',
        shape_name='EphemeralStorageSize',
    ))


@_dc.dataclass(frozen=True)
class FileSystemConfig(
    _base.Shape,
    shape_name='FileSystemConfig',
):
    arn: FileSystemArn = _dc.field(metadata=_base.field_metadata(
        member_name='Arn',
        shape_name='FileSystemArn',
    ))

    local_mount_path: LocalMountPath = _dc.field(metadata=_base.field_metadata(
        member_name='LocalMountPath',
        shape_name='LocalMountPath',
    ))


@_dc.dataclass(frozen=True)
class ImageConfigError(
    _base.Shape,
    shape_name='ImageConfigError',
):
    error_code: str = _dc.field(metadata=_base.field_metadata(
        member_name='ErrorCode',
        shape_name='String',
    ))

    message: SensitiveString = _dc.field(metadata=_base.field_metadata(
        member_name='Message',
        shape_name='SensitiveString',
    ))


@_dc.dataclass(frozen=True)
class InvalidParameterValueException(
    _base.Shape,
    shape_name='InvalidParameterValueException',
):
    type: str = _dc.field(metadata=_base.field_metadata(
        member_name='Type',
        shape_name='String',
    ))

    message: str = _dc.field(metadata=_base.field_metadata(
        member_name='message',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class Layer(
    _base.Shape,
    shape_name='Layer',
):
    arn: LayerVersionArn = _dc.field(metadata=_base.field_metadata(
        member_name='Arn',
        shape_name='LayerVersionArn',
    ))

    code_size: Long = _dc.field(metadata=_base.field_metadata(
        member_name='CodeSize',
        shape_name='Long',
    ))

    signing_profile_version_arn: Arn = _dc.field(metadata=_base.field_metadata(
        member_name='SigningProfileVersionArn',
        shape_name='Arn',
    ))

    signing_job_arn: Arn = _dc.field(metadata=_base.field_metadata(
        member_name='SigningJobArn',
        shape_name='Arn',
    ))


@_dc.dataclass(frozen=True)
class ListFunctionsRequest(
    _base.Shape,
    shape_name='ListFunctionsRequest',
):
    master_region: MasterRegion = _dc.field(metadata=_base.field_metadata(
        member_name='MasterRegion',
        shape_name='MasterRegion',
    ))

    function_version: FunctionVersion = _dc.field(metadata=_base.field_metadata(
        member_name='FunctionVersion',
        shape_name='FunctionVersion',
    ))

    marker: str = _dc.field(metadata=_base.field_metadata(
        member_name='Marker',
        shape_name='String',
    ))

    max_items: MaxListItems = _dc.field(metadata=_base.field_metadata(
        member_name='MaxItems',
        shape_name='MaxListItems',
    ))


@_dc.dataclass(frozen=True)
class LoggingConfig(
    _base.Shape,
    shape_name='LoggingConfig',
):
    log_format: LogFormat = _dc.field(metadata=_base.field_metadata(
        member_name='LogFormat',
        shape_name='LogFormat',
    ))

    application_log_level: ApplicationLogLevel = _dc.field(metadata=_base.field_metadata(
        member_name='ApplicationLogLevel',
        shape_name='ApplicationLogLevel',
    ))

    system_log_level: SystemLogLevel = _dc.field(metadata=_base.field_metadata(
        member_name='SystemLogLevel',
        shape_name='SystemLogLevel',
    ))

    log_group: LogGroup = _dc.field(metadata=_base.field_metadata(
        member_name='LogGroup',
        shape_name='LogGroup',
    ))


@_dc.dataclass(frozen=True)
class RuntimeVersionError(
    _base.Shape,
    shape_name='RuntimeVersionError',
):
    error_code: str = _dc.field(metadata=_base.field_metadata(
        member_name='ErrorCode',
        shape_name='String',
    ))

    message: SensitiveString = _dc.field(metadata=_base.field_metadata(
        member_name='Message',
        shape_name='SensitiveString',
    ))


SecurityGroupIds: _ta.TypeAlias = _ta.Sequence[SecurityGroupId]


@_dc.dataclass(frozen=True)
class ServiceException(
    _base.Shape,
    shape_name='ServiceException',
):
    type: str = _dc.field(metadata=_base.field_metadata(
        member_name='Type',
        shape_name='String',
    ))

    message: str = _dc.field(metadata=_base.field_metadata(
        member_name='Message',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class SnapStartResponse(
    _base.Shape,
    shape_name='SnapStartResponse',
):
    apply_on: SnapStartApplyOn = _dc.field(metadata=_base.field_metadata(
        member_name='ApplyOn',
        shape_name='SnapStartApplyOn',
    ))

    optimization_status: SnapStartOptimizationStatus = _dc.field(metadata=_base.field_metadata(
        member_name='OptimizationStatus',
        shape_name='SnapStartOptimizationStatus',
    ))


StringList: _ta.TypeAlias = _ta.Sequence[str]

SubnetIds: _ta.TypeAlias = _ta.Sequence[SubnetId]


@_dc.dataclass(frozen=True)
class TooManyRequestsException(
    _base.Shape,
    shape_name='TooManyRequestsException',
):
    retry_after_seconds: str = _dc.field(metadata=_base.field_metadata(
        member_name='retryAfterSeconds',
        shape_name='String',
    ))

    type: str = _dc.field(metadata=_base.field_metadata(
        member_name='Type',
        shape_name='String',
    ))

    message: str = _dc.field(metadata=_base.field_metadata(
        member_name='message',
        shape_name='String',
    ))

    reason: ThrottleReason = _dc.field(metadata=_base.field_metadata(
        member_name='Reason',
        shape_name='ThrottleReason',
    ))


@_dc.dataclass(frozen=True)
class TracingConfigResponse(
    _base.Shape,
    shape_name='TracingConfigResponse',
):
    mode: TracingMode = _dc.field(metadata=_base.field_metadata(
        member_name='Mode',
        shape_name='TracingMode',
    ))


@_dc.dataclass(frozen=True)
class EnvironmentResponse(
    _base.Shape,
    shape_name='EnvironmentResponse',
):
    variables: EnvironmentVariables = _dc.field(metadata=_base.field_metadata(
        member_name='Variables',
        shape_name='EnvironmentVariables',
    ))

    error: EnvironmentError_ = _dc.field(metadata=_base.field_metadata(
        member_name='Error',
        shape_name='EnvironmentError',
    ))


FileSystemConfigList: _ta.TypeAlias = _ta.Sequence[FileSystemConfig]


@_dc.dataclass(frozen=True)
class ImageConfig(
    _base.Shape,
    shape_name='ImageConfig',
):
    entry_point: StringList = _dc.field(metadata=_base.field_metadata(
        member_name='EntryPoint',
        shape_name='StringList',
    ))

    command: StringList = _dc.field(metadata=_base.field_metadata(
        member_name='Command',
        shape_name='StringList',
    ))

    working_directory: WorkingDirectory = _dc.field(metadata=_base.field_metadata(
        member_name='WorkingDirectory',
        shape_name='WorkingDirectory',
    ))


LayersReferenceList: _ta.TypeAlias = _ta.Sequence[Layer]


@_dc.dataclass(frozen=True)
class RuntimeVersionConfig(
    _base.Shape,
    shape_name='RuntimeVersionConfig',
):
    runtime_version_arn: RuntimeVersionArn = _dc.field(metadata=_base.field_metadata(
        member_name='RuntimeVersionArn',
        shape_name='RuntimeVersionArn',
    ))

    error: RuntimeVersionError = _dc.field(metadata=_base.field_metadata(
        member_name='Error',
        shape_name='RuntimeVersionError',
    ))


@_dc.dataclass(frozen=True)
class VpcConfigResponse(
    _base.Shape,
    shape_name='VpcConfigResponse',
):
    subnet_ids: SubnetIds = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetIds',
        shape_name='SubnetIds',
    ))

    security_group_ids: SecurityGroupIds = _dc.field(metadata=_base.field_metadata(
        member_name='SecurityGroupIds',
        shape_name='SecurityGroupIds',
    ))

    vpc_id: VpcId = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='VpcId',
    ))

    ipv6_allowed_for_dual_stack: NullableBoolean = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6AllowedForDualStack',
        shape_name='NullableBoolean',
    ))


@_dc.dataclass(frozen=True)
class ImageConfigResponse(
    _base.Shape,
    shape_name='ImageConfigResponse',
):
    image_config: ImageConfig = _dc.field(metadata=_base.field_metadata(
        member_name='ImageConfig',
        shape_name='ImageConfig',
    ))

    error: ImageConfigError = _dc.field(metadata=_base.field_metadata(
        member_name='Error',
        shape_name='ImageConfigError',
    ))


@_dc.dataclass(frozen=True)
class FunctionConfiguration(
    _base.Shape,
    shape_name='FunctionConfiguration',
):
    function_name: NamespacedFunctionName = _dc.field(metadata=_base.field_metadata(
        member_name='FunctionName',
        shape_name='NamespacedFunctionName',
    ))

    function_arn: NameSpacedFunctionArn = _dc.field(metadata=_base.field_metadata(
        member_name='FunctionArn',
        shape_name='NameSpacedFunctionArn',
    ))

    runtime: Runtime = _dc.field(metadata=_base.field_metadata(
        member_name='Runtime',
        shape_name='Runtime',
    ))

    role: RoleArn = _dc.field(metadata=_base.field_metadata(
        member_name='Role',
        shape_name='RoleArn',
    ))

    handler: Handler = _dc.field(metadata=_base.field_metadata(
        member_name='Handler',
        shape_name='Handler',
    ))

    code_size: Long = _dc.field(metadata=_base.field_metadata(
        member_name='CodeSize',
        shape_name='Long',
    ))

    description: Description = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='Description',
    ))

    timeout: Timeout = _dc.field(metadata=_base.field_metadata(
        member_name='Timeout',
        shape_name='Timeout',
    ))

    memory_size: MemorySize = _dc.field(metadata=_base.field_metadata(
        member_name='MemorySize',
        shape_name='MemorySize',
    ))

    last_modified: Timestamp = _dc.field(metadata=_base.field_metadata(
        member_name='LastModified',
        shape_name='Timestamp',
    ))

    code_sha256: str = _dc.field(metadata=_base.field_metadata(
        member_name='CodeSha256',
        shape_name='String',
    ))

    version: Version = _dc.field(metadata=_base.field_metadata(
        member_name='Version',
        shape_name='Version',
    ))

    vpc_config: VpcConfigResponse = _dc.field(metadata=_base.field_metadata(
        member_name='VpcConfig',
        shape_name='VpcConfigResponse',
    ))

    dead_letter_config: DeadLetterConfig = _dc.field(metadata=_base.field_metadata(
        member_name='DeadLetterConfig',
        shape_name='DeadLetterConfig',
    ))

    environment: EnvironmentResponse = _dc.field(metadata=_base.field_metadata(
        member_name='Environment',
        shape_name='EnvironmentResponse',
    ))

    kms_key_arn: KMSKeyArn = _dc.field(metadata=_base.field_metadata(
        member_name='KMSKeyArn',
        shape_name='KMSKeyArn',
    ))

    tracing_config: TracingConfigResponse = _dc.field(metadata=_base.field_metadata(
        member_name='TracingConfig',
        shape_name='TracingConfigResponse',
    ))

    master_arn: FunctionArn = _dc.field(metadata=_base.field_metadata(
        member_name='MasterArn',
        shape_name='FunctionArn',
    ))

    revision_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='RevisionId',
        shape_name='String',
    ))

    layers: LayersReferenceList = _dc.field(metadata=_base.field_metadata(
        member_name='Layers',
        shape_name='LayersReferenceList',
    ))

    state: State = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='State',
    ))

    state_reason: StateReason = _dc.field(metadata=_base.field_metadata(
        member_name='StateReason',
        shape_name='StateReason',
    ))

    state_reason_code: StateReasonCode = _dc.field(metadata=_base.field_metadata(
        member_name='StateReasonCode',
        shape_name='StateReasonCode',
    ))

    last_update_status: LastUpdateStatus = _dc.field(metadata=_base.field_metadata(
        member_name='LastUpdateStatus',
        shape_name='LastUpdateStatus',
    ))

    last_update_status_reason: LastUpdateStatusReason = _dc.field(metadata=_base.field_metadata(
        member_name='LastUpdateStatusReason',
        shape_name='LastUpdateStatusReason',
    ))

    last_update_status_reason_code: LastUpdateStatusReasonCode = _dc.field(metadata=_base.field_metadata(
        member_name='LastUpdateStatusReasonCode',
        shape_name='LastUpdateStatusReasonCode',
    ))

    file_system_configs: FileSystemConfigList = _dc.field(metadata=_base.field_metadata(
        member_name='FileSystemConfigs',
        shape_name='FileSystemConfigList',
    ))

    package_type: PackageType = _dc.field(metadata=_base.field_metadata(
        member_name='PackageType',
        shape_name='PackageType',
    ))

    image_config_response: ImageConfigResponse = _dc.field(metadata=_base.field_metadata(
        member_name='ImageConfigResponse',
        shape_name='ImageConfigResponse',
    ))

    signing_profile_version_arn: Arn = _dc.field(metadata=_base.field_metadata(
        member_name='SigningProfileVersionArn',
        shape_name='Arn',
    ))

    signing_job_arn: Arn = _dc.field(metadata=_base.field_metadata(
        member_name='SigningJobArn',
        shape_name='Arn',
    ))

    architectures: ArchitecturesList = _dc.field(metadata=_base.field_metadata(
        member_name='Architectures',
        shape_name='ArchitecturesList',
    ))

    ephemeral_storage: EphemeralStorage = _dc.field(metadata=_base.field_metadata(
        member_name='EphemeralStorage',
        shape_name='EphemeralStorage',
    ))

    snap_start: SnapStartResponse = _dc.field(metadata=_base.field_metadata(
        member_name='SnapStart',
        shape_name='SnapStartResponse',
    ))

    runtime_version_config: RuntimeVersionConfig = _dc.field(metadata=_base.field_metadata(
        member_name='RuntimeVersionConfig',
        shape_name='RuntimeVersionConfig',
    ))

    logging_config: LoggingConfig = _dc.field(metadata=_base.field_metadata(
        member_name='LoggingConfig',
        shape_name='LoggingConfig',
    ))


FunctionList: _ta.TypeAlias = _ta.Sequence[FunctionConfiguration]


@_dc.dataclass(frozen=True)
class ListFunctionsResponse(
    _base.Shape,
    shape_name='ListFunctionsResponse',
):
    next_marker: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextMarker',
        shape_name='String',
    ))

    functions: FunctionList = _dc.field(metadata=_base.field_metadata(
        member_name='Functions',
        shape_name='FunctionList',
    ))


ALL_SHAPES: frozenset[type[_base.Shape]] = frozenset([
    DeadLetterConfig,
    EnvironmentError_,
    EnvironmentResponse,
    EphemeralStorage,
    FileSystemConfig,
    FunctionConfiguration,
    ImageConfig,
    ImageConfigError,
    ImageConfigResponse,
    InvalidParameterValueException,
    Layer,
    ListFunctionsRequest,
    ListFunctionsResponse,
    LoggingConfig,
    RuntimeVersionConfig,
    RuntimeVersionError,
    ServiceException,
    SnapStartResponse,
    TooManyRequestsException,
    TracingConfigResponse,
    VpcConfigResponse,
])


##


LIST_FUNCTIONS = _base.Operation(
    name='ListFunctions',
    input=ListFunctionsRequest,
    output=ListFunctionsResponse,
    errors=[
        InvalidParameterValueException,
        ServiceException,
        TooManyRequestsException,
    ],
)


ALL_OPERATIONS: frozenset[_base.Operation] = frozenset([
    LIST_FUNCTIONS,
])