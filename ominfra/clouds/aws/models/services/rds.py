# flake8: noqa: E501
# ruff: noqa: N801 S105
# fmt: off
import dataclasses as _dc  # noqa
import enum as _enum  # noqa
import typing as _ta  # noqa

from .. import base as _base  # noqa


##


class ActivityStreamMode(_enum.Enum):
    SYNC = 'sync'
    ASYNC = 'async'


class ActivityStreamPolicyStatus(_enum.Enum):
    LOCKED = 'locked'
    UNLOCKED = 'unlocked'
    LOCKING_POLICY = 'locking-policy'
    UNLOCKING_POLICY = 'unlocking-policy'


class ActivityStreamStatus(_enum.Enum):
    STOPPED = 'stopped'
    STARTING = 'starting'
    STARTED = 'started'
    STOPPING = 'stopping'


@_dc.dataclass(frozen=True)
class AuthorizationNotFoundFault(
    _base.Shape,
    shape_name='AuthorizationNotFoundFault',
):
    pass


class AutomationMode(_enum.Enum):
    FULL = 'full'
    ALL_PAUSED = 'all-paused'


@_dc.dataclass(frozen=True)
class BackupPolicyNotFoundFault(
    _base.Shape,
    shape_name='BackupPolicyNotFoundFault',
):
    pass


BooleanOptional = _ta.NewType('BooleanOptional', bool)


@_dc.dataclass(frozen=True)
class CertificateNotFoundFault(
    _base.Shape,
    shape_name='CertificateNotFoundFault',
):
    pass


@_dc.dataclass(frozen=True)
class DBClusterNotFoundFault(
    _base.Shape,
    shape_name='DBClusterNotFoundFault',
):
    pass


@_dc.dataclass(frozen=True)
class DBInstanceAlreadyExistsFault(
    _base.Shape,
    shape_name='DBInstanceAlreadyExistsFault',
):
    pass


@_dc.dataclass(frozen=True)
class DBInstanceAutomatedBackupQuotaExceededFault(
    _base.Shape,
    shape_name='DBInstanceAutomatedBackupQuotaExceededFault',
):
    pass


@_dc.dataclass(frozen=True)
class DBInstanceNotFoundFault(
    _base.Shape,
    shape_name='DBInstanceNotFoundFault',
):
    pass


@_dc.dataclass(frozen=True)
class DBParameterGroupNotFoundFault(
    _base.Shape,
    shape_name='DBParameterGroupNotFoundFault',
):
    pass


@_dc.dataclass(frozen=True)
class DBSecurityGroupNotFoundFault(
    _base.Shape,
    shape_name='DBSecurityGroupNotFoundFault',
):
    pass


@_dc.dataclass(frozen=True)
class DBSnapshotAlreadyExistsFault(
    _base.Shape,
    shape_name='DBSnapshotAlreadyExistsFault',
):
    pass


@_dc.dataclass(frozen=True)
class DBSubnetGroupDoesNotCoverEnoughAZs(
    _base.Shape,
    shape_name='DBSubnetGroupDoesNotCoverEnoughAZs',
):
    pass


@_dc.dataclass(frozen=True)
class DBSubnetGroupNotFoundFault(
    _base.Shape,
    shape_name='DBSubnetGroupNotFoundFault',
):
    pass


class DatabaseInsightsMode(_enum.Enum):
    STANDARD = 'standard'
    ADVANCED = 'advanced'


@_dc.dataclass(frozen=True)
class DomainNotFoundFault(
    _base.Shape,
    shape_name='DomainNotFoundFault',
):
    pass


@_dc.dataclass(frozen=True)
class InstanceQuotaExceededFault(
    _base.Shape,
    shape_name='InstanceQuotaExceededFault',
):
    pass


@_dc.dataclass(frozen=True)
class InsufficientDBInstanceCapacityFault(
    _base.Shape,
    shape_name='InsufficientDBInstanceCapacityFault',
):
    pass


IntegerOptional = _ta.NewType('IntegerOptional', int)


@_dc.dataclass(frozen=True)
class InvalidDBClusterStateFault(
    _base.Shape,
    shape_name='InvalidDBClusterStateFault',
):
    pass


@_dc.dataclass(frozen=True)
class InvalidDBInstanceStateFault(
    _base.Shape,
    shape_name='InvalidDBInstanceStateFault',
):
    pass


@_dc.dataclass(frozen=True)
class InvalidSubnet(
    _base.Shape,
    shape_name='InvalidSubnet',
):
    pass


@_dc.dataclass(frozen=True)
class InvalidVPCNetworkStateFault(
    _base.Shape,
    shape_name='InvalidVPCNetworkStateFault',
):
    pass


@_dc.dataclass(frozen=True)
class KMSKeyNotAccessibleFault(
    _base.Shape,
    shape_name='KMSKeyNotAccessibleFault',
):
    pass


@_dc.dataclass(frozen=True)
class NetworkTypeNotSupported(
    _base.Shape,
    shape_name='NetworkTypeNotSupported',
):
    pass


@_dc.dataclass(frozen=True)
class OptionGroupNotFoundFault(
    _base.Shape,
    shape_name='OptionGroupNotFoundFault',
):
    pass


@_dc.dataclass(frozen=True)
class ProvisionedIopsNotAvailableInAZFault(
    _base.Shape,
    shape_name='ProvisionedIopsNotAvailableInAZFault',
):
    pass


class ReplicaMode(_enum.Enum):
    OPEN_READ_ONLY = 'open-read-only'
    MOUNTED = 'mounted'


@_dc.dataclass(frozen=True)
class SnapshotQuotaExceededFault(
    _base.Shape,
    shape_name='SnapshotQuotaExceededFault',
):
    pass


@_dc.dataclass(frozen=True)
class StorageQuotaExceededFault(
    _base.Shape,
    shape_name='StorageQuotaExceededFault',
):
    pass


@_dc.dataclass(frozen=True)
class StorageTypeNotSupportedFault(
    _base.Shape,
    shape_name='StorageTypeNotSupportedFault',
):
    pass


TStamp = _ta.NewType('TStamp', _base.Timestamp)


@_dc.dataclass(frozen=True)
class TenantDatabaseQuotaExceededFault(
    _base.Shape,
    shape_name='TenantDatabaseQuotaExceededFault',
):
    pass


@_dc.dataclass(frozen=True)
class AvailabilityZone(
    _base.Shape,
    shape_name='AvailabilityZone',
):
    name: str = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class CertificateDetails(
    _base.Shape,
    shape_name='CertificateDetails',
):
    ca_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='CAIdentifier',
        shape_name='String',
    ))

    valid_till: TStamp = _dc.field(metadata=_base.field_metadata(
        member_name='ValidTill',
        shape_name='TStamp',
    ))


@_dc.dataclass(frozen=True)
class DBInstanceAutomatedBackupsReplication(
    _base.Shape,
    shape_name='DBInstanceAutomatedBackupsReplication',
):
    db_instance_automated_backups_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceAutomatedBackupsArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class DBInstanceRole(
    _base.Shape,
    shape_name='DBInstanceRole',
):
    role_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='RoleArn',
        shape_name='String',
    ))

    feature_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='FeatureName',
        shape_name='String',
    ))

    status: str = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class DBInstanceStatusInfo(
    _base.Shape,
    shape_name='DBInstanceStatusInfo',
):
    status_type: str = _dc.field(metadata=_base.field_metadata(
        member_name='StatusType',
        shape_name='String',
    ))

    normal: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Normal',
        shape_name='Boolean',
    ))

    status: str = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='String',
    ))

    message: str = _dc.field(metadata=_base.field_metadata(
        member_name='Message',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class DBParameterGroupStatus(
    _base.Shape,
    shape_name='DBParameterGroupStatus',
):
    db_parameter_group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBParameterGroupName',
        shape_name='String',
    ))

    parameter_apply_status: str = _dc.field(metadata=_base.field_metadata(
        member_name='ParameterApplyStatus',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class DBSecurityGroupMembership(
    _base.Shape,
    shape_name='DBSecurityGroupMembership',
):
    db_security_group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSecurityGroupName',
        shape_name='String',
    ))

    status: str = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='String',
    ))


DBSecurityGroupNameList: _ta.TypeAlias = _ta.Sequence[str]


@_dc.dataclass(frozen=True)
class DeleteDBInstanceMessage(
    _base.Shape,
    shape_name='DeleteDBInstanceMessage',
):
    db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceIdentifier',
        shape_name='String',
    ))

    skip_final_snapshot: bool = _dc.field(metadata=_base.field_metadata(
        member_name='SkipFinalSnapshot',
        shape_name='Boolean',
    ))

    final_db_snapshot_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='FinalDBSnapshotIdentifier',
        shape_name='String',
    ))

    delete_automated_backups: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='DeleteAutomatedBackups',
        shape_name='BooleanOptional',
    ))


@_dc.dataclass(frozen=True)
class Endpoint(
    _base.Shape,
    shape_name='Endpoint',
):
    address: str = _dc.field(metadata=_base.field_metadata(
        member_name='Address',
        shape_name='String',
    ))

    port: int = _dc.field(metadata=_base.field_metadata(
        member_name='Port',
        shape_name='Integer',
    ))

    hosted_zone_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='HostedZoneId',
        shape_name='String',
    ))


FilterValueList: _ta.TypeAlias = _ta.Sequence[str]

LogTypeList: _ta.TypeAlias = _ta.Sequence[str]


@_dc.dataclass(frozen=True)
class MasterUserSecret(
    _base.Shape,
    shape_name='MasterUserSecret',
):
    secret_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='SecretArn',
        shape_name='String',
    ))

    secret_status: str = _dc.field(metadata=_base.field_metadata(
        member_name='SecretStatus',
        shape_name='String',
    ))

    kms_key_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='KmsKeyId',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class OptionGroupMembership(
    _base.Shape,
    shape_name='OptionGroupMembership',
):
    option_group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='OptionGroupName',
        shape_name='String',
    ))

    status: str = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class Outpost(
    _base.Shape,
    shape_name='Outpost',
):
    arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='Arn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class ProcessorFeature(
    _base.Shape,
    shape_name='ProcessorFeature',
):
    name: str = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='String',
    ))

    value: str = _dc.field(metadata=_base.field_metadata(
        member_name='Value',
        shape_name='String',
    ))


ReadReplicaDBClusterIdentifierList: _ta.TypeAlias = _ta.Sequence[str]

ReadReplicaDBInstanceIdentifierList: _ta.TypeAlias = _ta.Sequence[str]


@_dc.dataclass(frozen=True)
class RebootDBInstanceMessage(
    _base.Shape,
    shape_name='RebootDBInstanceMessage',
):
    db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceIdentifier',
        shape_name='String',
    ))

    force_failover: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='ForceFailover',
        shape_name='BooleanOptional',
    ))


@_dc.dataclass(frozen=True)
class StartDBInstanceMessage(
    _base.Shape,
    shape_name='StartDBInstanceMessage',
):
    db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceIdentifier',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class StopDBInstanceMessage(
    _base.Shape,
    shape_name='StopDBInstanceMessage',
):
    db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceIdentifier',
        shape_name='String',
    ))

    db_snapshot_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSnapshotIdentifier',
        shape_name='String',
    ))


StringList: _ta.TypeAlias = _ta.Sequence[str]

VpcSecurityGroupIdList: _ta.TypeAlias = _ta.Sequence[str]


@_dc.dataclass(frozen=True)
class VpcSecurityGroupMembership(
    _base.Shape,
    shape_name='VpcSecurityGroupMembership',
):
    vpc_security_group_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcSecurityGroupId',
        shape_name='String',
    ))

    status: str = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='String',
    ))


DBInstanceAutomatedBackupsReplicationList: _ta.TypeAlias = _ta.Sequence[DBInstanceAutomatedBackupsReplication]

DBInstanceRoles: _ta.TypeAlias = _ta.Sequence[DBInstanceRole]

DBInstanceStatusInfoList: _ta.TypeAlias = _ta.Sequence[DBInstanceStatusInfo]

DBParameterGroupStatusList: _ta.TypeAlias = _ta.Sequence[DBParameterGroupStatus]

DBSecurityGroupMembershipList: _ta.TypeAlias = _ta.Sequence[DBSecurityGroupMembership]


@_dc.dataclass(frozen=True)
class DomainMembership(
    _base.Shape,
    shape_name='DomainMembership',
):
    domain: str = _dc.field(metadata=_base.field_metadata(
        member_name='Domain',
        shape_name='String',
    ))

    status: str = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='String',
    ))

    f_q_d_n: str = _dc.field(metadata=_base.field_metadata(
        member_name='FQDN',
        shape_name='String',
    ))

    iam_role_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='IAMRoleName',
        shape_name='String',
    ))

    o_u: str = _dc.field(metadata=_base.field_metadata(
        member_name='OU',
        shape_name='String',
    ))

    auth_secret_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='AuthSecretArn',
        shape_name='String',
    ))

    dns_ips: StringList = _dc.field(metadata=_base.field_metadata(
        member_name='DnsIps',
        shape_name='StringList',
    ))


@_dc.dataclass(frozen=True)
class Filter(
    _base.Shape,
    shape_name='Filter',
):
    name: str = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='String',
    ))

    values: FilterValueList = _dc.field(metadata=_base.field_metadata(
        member_name='Values',
        shape_name='FilterValueList',
    ))


OptionGroupMembershipList: _ta.TypeAlias = _ta.Sequence[OptionGroupMembership]


@_dc.dataclass(frozen=True)
class PendingCloudwatchLogsExports(
    _base.Shape,
    shape_name='PendingCloudwatchLogsExports',
):
    log_types_to_enable: LogTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='LogTypesToEnable',
        shape_name='LogTypeList',
    ))

    log_types_to_disable: LogTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='LogTypesToDisable',
        shape_name='LogTypeList',
    ))


ProcessorFeatureList: _ta.TypeAlias = _ta.Sequence[ProcessorFeature]


@_dc.dataclass(frozen=True)
class Subnet(
    _base.Shape,
    shape_name='Subnet',
):
    subnet_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetIdentifier',
        shape_name='String',
    ))

    subnet_availability_zone: AvailabilityZone = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetAvailabilityZone',
        shape_name='AvailabilityZone',
    ))

    subnet_outpost: Outpost = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetOutpost',
        shape_name='Outpost',
    ))

    subnet_status: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetStatus',
        shape_name='String',
    ))


VpcSecurityGroupMembershipList: _ta.TypeAlias = _ta.Sequence[VpcSecurityGroupMembership]


@_dc.dataclass(frozen=True)
class CreateDBInstanceMessage(
    _base.Shape,
    shape_name='CreateDBInstanceMessage',
):
    db_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBName',
        shape_name='String',
    ))

    db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceIdentifier',
        shape_name='String',
    ))

    allocated_storage: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='AllocatedStorage',
        shape_name='IntegerOptional',
    ))

    db_instance_class: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceClass',
        shape_name='String',
    ))

    engine: str = _dc.field(metadata=_base.field_metadata(
        member_name='Engine',
        shape_name='String',
    ))

    master_username: str = _dc.field(metadata=_base.field_metadata(
        member_name='MasterUsername',
        shape_name='String',
    ))

    master_user_password: str = _dc.field(metadata=_base.field_metadata(
        member_name='MasterUserPassword',
        shape_name='String',
    ))

    db_security_groups: DBSecurityGroupNameList = _dc.field(metadata=_base.field_metadata(
        member_name='DBSecurityGroups',
        shape_name='DBSecurityGroupNameList',
    ))

    vpc_security_group_ids: VpcSecurityGroupIdList = _dc.field(metadata=_base.field_metadata(
        member_name='VpcSecurityGroupIds',
        shape_name='VpcSecurityGroupIdList',
    ))

    availability_zone: str = _dc.field(metadata=_base.field_metadata(
        member_name='AvailabilityZone',
        shape_name='String',
    ))

    db_subnet_group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSubnetGroupName',
        shape_name='String',
    ))

    preferred_maintenance_window: str = _dc.field(metadata=_base.field_metadata(
        member_name='PreferredMaintenanceWindow',
        shape_name='String',
    ))

    db_parameter_group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBParameterGroupName',
        shape_name='String',
    ))

    backup_retention_period: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='BackupRetentionPeriod',
        shape_name='IntegerOptional',
    ))

    preferred_backup_window: str = _dc.field(metadata=_base.field_metadata(
        member_name='PreferredBackupWindow',
        shape_name='String',
    ))

    port: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='Port',
        shape_name='IntegerOptional',
    ))

    multi_az: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MultiAZ',
        shape_name='BooleanOptional',
    ))

    engine_version: str = _dc.field(metadata=_base.field_metadata(
        member_name='EngineVersion',
        shape_name='String',
    ))

    auto_minor_version_upgrade: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='AutoMinorVersionUpgrade',
        shape_name='BooleanOptional',
    ))

    license_model: str = _dc.field(metadata=_base.field_metadata(
        member_name='LicenseModel',
        shape_name='String',
    ))

    iops: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='Iops',
        shape_name='IntegerOptional',
    ))

    option_group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='OptionGroupName',
        shape_name='String',
    ))

    character_set_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='CharacterSetName',
        shape_name='String',
    ))

    nchar_character_set_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='NcharCharacterSetName',
        shape_name='String',
    ))

    publicly_accessible: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='PubliclyAccessible',
        shape_name='BooleanOptional',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))

    db_cluster_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBClusterIdentifier',
        shape_name='String',
    ))

    storage_type: str = _dc.field(metadata=_base.field_metadata(
        member_name='StorageType',
        shape_name='String',
    ))

    tde_credential_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='TdeCredentialArn',
        shape_name='String',
    ))

    tde_credential_password: str = _dc.field(metadata=_base.field_metadata(
        member_name='TdeCredentialPassword',
        shape_name='String',
    ))

    storage_encrypted: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='StorageEncrypted',
        shape_name='BooleanOptional',
    ))

    kms_key_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='KmsKeyId',
        shape_name='String',
    ))

    domain: str = _dc.field(metadata=_base.field_metadata(
        member_name='Domain',
        shape_name='String',
    ))

    domain_fqdn: str = _dc.field(metadata=_base.field_metadata(
        member_name='DomainFqdn',
        shape_name='String',
    ))

    domain_ou: str = _dc.field(metadata=_base.field_metadata(
        member_name='DomainOu',
        shape_name='String',
    ))

    domain_auth_secret_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='DomainAuthSecretArn',
        shape_name='String',
    ))

    domain_dns_ips: StringList = _dc.field(metadata=_base.field_metadata(
        member_name='DomainDnsIps',
        shape_name='StringList',
    ))

    copy_tags_to_snapshot: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='CopyTagsToSnapshot',
        shape_name='BooleanOptional',
    ))

    monitoring_interval: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MonitoringInterval',
        shape_name='IntegerOptional',
    ))

    monitoring_role_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='MonitoringRoleArn',
        shape_name='String',
    ))

    domain_iam_role_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DomainIAMRoleName',
        shape_name='String',
    ))

    promotion_tier: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='PromotionTier',
        shape_name='IntegerOptional',
    ))

    timezone: str = _dc.field(metadata=_base.field_metadata(
        member_name='Timezone',
        shape_name='String',
    ))

    enable_iam_database_authentication: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='EnableIAMDatabaseAuthentication',
        shape_name='BooleanOptional',
    ))

    database_insights_mode: DatabaseInsightsMode = _dc.field(metadata=_base.field_metadata(
        member_name='DatabaseInsightsMode',
        shape_name='DatabaseInsightsMode',
    ))

    enable_performance_insights: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='EnablePerformanceInsights',
        shape_name='BooleanOptional',
    ))

    performance_insights_kms_key_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='PerformanceInsightsKMSKeyId',
        shape_name='String',
    ))

    performance_insights_retention_period: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='PerformanceInsightsRetentionPeriod',
        shape_name='IntegerOptional',
    ))

    enable_cloudwatch_logs_exports: LogTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='EnableCloudwatchLogsExports',
        shape_name='LogTypeList',
    ))

    processor_features: ProcessorFeatureList = _dc.field(metadata=_base.field_metadata(
        member_name='ProcessorFeatures',
        shape_name='ProcessorFeatureList',
    ))

    deletion_protection: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='DeletionProtection',
        shape_name='BooleanOptional',
    ))

    max_allocated_storage: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MaxAllocatedStorage',
        shape_name='IntegerOptional',
    ))

    enable_customer_owned_ip: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='EnableCustomerOwnedIp',
        shape_name='BooleanOptional',
    ))

    custom_iam_instance_profile: str = _dc.field(metadata=_base.field_metadata(
        member_name='CustomIamInstanceProfile',
        shape_name='String',
    ))

    backup_target: str = _dc.field(metadata=_base.field_metadata(
        member_name='BackupTarget',
        shape_name='String',
    ))

    network_type: str = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkType',
        shape_name='String',
    ))

    storage_throughput: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='StorageThroughput',
        shape_name='IntegerOptional',
    ))

    manage_master_user_password: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='ManageMasterUserPassword',
        shape_name='BooleanOptional',
    ))

    master_user_secret_kms_key_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='MasterUserSecretKmsKeyId',
        shape_name='String',
    ))

    ca_certificate_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='CACertificateIdentifier',
        shape_name='String',
    ))

    db_system_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSystemId',
        shape_name='String',
    ))

    dedicated_log_volume: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='DedicatedLogVolume',
        shape_name='BooleanOptional',
    ))

    multi_tenant: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MultiTenant',
        shape_name='BooleanOptional',
    ))

    engine_lifecycle_support: str = _dc.field(metadata=_base.field_metadata(
        member_name='EngineLifecycleSupport',
        shape_name='String',
    ))


DomainMembershipList: _ta.TypeAlias = _ta.Sequence[DomainMembership]

FilterList: _ta.TypeAlias = _ta.Sequence[Filter]


@_dc.dataclass(frozen=True)
class PendingModifiedValues(
    _base.Shape,
    shape_name='PendingModifiedValues',
):
    db_instance_class: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceClass',
        shape_name='String',
    ))

    allocated_storage: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='AllocatedStorage',
        shape_name='IntegerOptional',
    ))

    master_user_password: str = _dc.field(metadata=_base.field_metadata(
        member_name='MasterUserPassword',
        shape_name='String',
    ))

    port: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='Port',
        shape_name='IntegerOptional',
    ))

    backup_retention_period: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='BackupRetentionPeriod',
        shape_name='IntegerOptional',
    ))

    multi_az: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MultiAZ',
        shape_name='BooleanOptional',
    ))

    engine_version: str = _dc.field(metadata=_base.field_metadata(
        member_name='EngineVersion',
        shape_name='String',
    ))

    license_model: str = _dc.field(metadata=_base.field_metadata(
        member_name='LicenseModel',
        shape_name='String',
    ))

    iops: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='Iops',
        shape_name='IntegerOptional',
    ))

    db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceIdentifier',
        shape_name='String',
    ))

    storage_type: str = _dc.field(metadata=_base.field_metadata(
        member_name='StorageType',
        shape_name='String',
    ))

    ca_certificate_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='CACertificateIdentifier',
        shape_name='String',
    ))

    db_subnet_group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSubnetGroupName',
        shape_name='String',
    ))

    pending_cloudwatch_logs_exports: PendingCloudwatchLogsExports = _dc.field(metadata=_base.field_metadata(
        member_name='PendingCloudwatchLogsExports',
        shape_name='PendingCloudwatchLogsExports',
    ))

    processor_features: ProcessorFeatureList = _dc.field(metadata=_base.field_metadata(
        member_name='ProcessorFeatures',
        shape_name='ProcessorFeatureList',
    ))

    iam_database_authentication_enabled: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='IAMDatabaseAuthenticationEnabled',
        shape_name='BooleanOptional',
    ))

    automation_mode: AutomationMode = _dc.field(metadata=_base.field_metadata(
        member_name='AutomationMode',
        shape_name='AutomationMode',
    ))

    resume_full_automation_mode_time: TStamp = _dc.field(metadata=_base.field_metadata(
        member_name='ResumeFullAutomationModeTime',
        shape_name='TStamp',
    ))

    storage_throughput: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='StorageThroughput',
        shape_name='IntegerOptional',
    ))

    engine: str = _dc.field(metadata=_base.field_metadata(
        member_name='Engine',
        shape_name='String',
    ))

    dedicated_log_volume: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='DedicatedLogVolume',
        shape_name='BooleanOptional',
    ))

    multi_tenant: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MultiTenant',
        shape_name='BooleanOptional',
    ))


SubnetList: _ta.TypeAlias = _ta.Sequence[Subnet]


@_dc.dataclass(frozen=True)
class DBSubnetGroup(
    _base.Shape,
    shape_name='DBSubnetGroup',
):
    db_subnet_group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSubnetGroupName',
        shape_name='String',
    ))

    db_subnet_group_description: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSubnetGroupDescription',
        shape_name='String',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))

    subnet_group_status: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetGroupStatus',
        shape_name='String',
    ))

    subnets: SubnetList = _dc.field(metadata=_base.field_metadata(
        member_name='Subnets',
        shape_name='SubnetList',
    ))

    db_subnet_group_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSubnetGroupArn',
        shape_name='String',
    ))

    supported_network_types: StringList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedNetworkTypes',
        shape_name='StringList',
    ))


@_dc.dataclass(frozen=True)
class DescribeDBInstancesMessage(
    _base.Shape,
    shape_name='DescribeDBInstancesMessage',
):
    db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceIdentifier',
        shape_name='String',
    ))

    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))

    max_records: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MaxRecords',
        shape_name='IntegerOptional',
    ))

    marker: str = _dc.field(metadata=_base.field_metadata(
        member_name='Marker',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class DBInstance(
    _base.Shape,
    shape_name='DBInstance',
):
    db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceIdentifier',
        shape_name='String',
    ))

    db_instance_class: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceClass',
        shape_name='String',
    ))

    engine: str = _dc.field(metadata=_base.field_metadata(
        member_name='Engine',
        shape_name='String',
    ))

    db_instance_status: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceStatus',
        shape_name='String',
    ))

    automatic_restart_time: TStamp = _dc.field(metadata=_base.field_metadata(
        member_name='AutomaticRestartTime',
        shape_name='TStamp',
    ))

    master_username: str = _dc.field(metadata=_base.field_metadata(
        member_name='MasterUsername',
        shape_name='String',
    ))

    db_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBName',
        shape_name='String',
    ))

    endpoint: Endpoint = _dc.field(metadata=_base.field_metadata(
        member_name='Endpoint',
        shape_name='Endpoint',
    ))

    allocated_storage: int = _dc.field(metadata=_base.field_metadata(
        member_name='AllocatedStorage',
        shape_name='Integer',
    ))

    instance_create_time: TStamp = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceCreateTime',
        shape_name='TStamp',
    ))

    preferred_backup_window: str = _dc.field(metadata=_base.field_metadata(
        member_name='PreferredBackupWindow',
        shape_name='String',
    ))

    backup_retention_period: int = _dc.field(metadata=_base.field_metadata(
        member_name='BackupRetentionPeriod',
        shape_name='Integer',
    ))

    db_security_groups: DBSecurityGroupMembershipList = _dc.field(metadata=_base.field_metadata(
        member_name='DBSecurityGroups',
        shape_name='DBSecurityGroupMembershipList',
    ))

    vpc_security_groups: VpcSecurityGroupMembershipList = _dc.field(metadata=_base.field_metadata(
        member_name='VpcSecurityGroups',
        shape_name='VpcSecurityGroupMembershipList',
    ))

    db_parameter_groups: DBParameterGroupStatusList = _dc.field(metadata=_base.field_metadata(
        member_name='DBParameterGroups',
        shape_name='DBParameterGroupStatusList',
    ))

    availability_zone: str = _dc.field(metadata=_base.field_metadata(
        member_name='AvailabilityZone',
        shape_name='String',
    ))

    db_subnet_group: DBSubnetGroup = _dc.field(metadata=_base.field_metadata(
        member_name='DBSubnetGroup',
        shape_name='DBSubnetGroup',
    ))

    preferred_maintenance_window: str = _dc.field(metadata=_base.field_metadata(
        member_name='PreferredMaintenanceWindow',
        shape_name='String',
    ))

    pending_modified_values: PendingModifiedValues = _dc.field(metadata=_base.field_metadata(
        member_name='PendingModifiedValues',
        shape_name='PendingModifiedValues',
    ))

    latest_restorable_time: TStamp = _dc.field(metadata=_base.field_metadata(
        member_name='LatestRestorableTime',
        shape_name='TStamp',
    ))

    multi_az: bool = _dc.field(metadata=_base.field_metadata(
        member_name='MultiAZ',
        shape_name='Boolean',
    ))

    engine_version: str = _dc.field(metadata=_base.field_metadata(
        member_name='EngineVersion',
        shape_name='String',
    ))

    auto_minor_version_upgrade: bool = _dc.field(metadata=_base.field_metadata(
        member_name='AutoMinorVersionUpgrade',
        shape_name='Boolean',
    ))

    read_replica_source_db_instance_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='ReadReplicaSourceDBInstanceIdentifier',
        shape_name='String',
    ))

    read_replica_db_instance_identifiers: ReadReplicaDBInstanceIdentifierList = _dc.field(metadata=_base.field_metadata(
        member_name='ReadReplicaDBInstanceIdentifiers',
        shape_name='ReadReplicaDBInstanceIdentifierList',
    ))

    read_replica_db_cluster_identifiers: ReadReplicaDBClusterIdentifierList = _dc.field(metadata=_base.field_metadata(
        member_name='ReadReplicaDBClusterIdentifiers',
        shape_name='ReadReplicaDBClusterIdentifierList',
    ))

    replica_mode: ReplicaMode = _dc.field(metadata=_base.field_metadata(
        member_name='ReplicaMode',
        shape_name='ReplicaMode',
    ))

    license_model: str = _dc.field(metadata=_base.field_metadata(
        member_name='LicenseModel',
        shape_name='String',
    ))

    iops: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='Iops',
        shape_name='IntegerOptional',
    ))

    option_group_memberships: OptionGroupMembershipList = _dc.field(metadata=_base.field_metadata(
        member_name='OptionGroupMemberships',
        shape_name='OptionGroupMembershipList',
    ))

    character_set_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='CharacterSetName',
        shape_name='String',
    ))

    nchar_character_set_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='NcharCharacterSetName',
        shape_name='String',
    ))

    secondary_availability_zone: str = _dc.field(metadata=_base.field_metadata(
        member_name='SecondaryAvailabilityZone',
        shape_name='String',
    ))

    publicly_accessible: bool = _dc.field(metadata=_base.field_metadata(
        member_name='PubliclyAccessible',
        shape_name='Boolean',
    ))

    status_infos: DBInstanceStatusInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='StatusInfos',
        shape_name='DBInstanceStatusInfoList',
    ))

    storage_type: str = _dc.field(metadata=_base.field_metadata(
        member_name='StorageType',
        shape_name='String',
    ))

    tde_credential_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='TdeCredentialArn',
        shape_name='String',
    ))

    db_instance_port: int = _dc.field(metadata=_base.field_metadata(
        member_name='DbInstancePort',
        shape_name='Integer',
    ))

    db_cluster_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBClusterIdentifier',
        shape_name='String',
    ))

    storage_encrypted: bool = _dc.field(metadata=_base.field_metadata(
        member_name='StorageEncrypted',
        shape_name='Boolean',
    ))

    kms_key_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='KmsKeyId',
        shape_name='String',
    ))

    dbi_resource_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='DbiResourceId',
        shape_name='String',
    ))

    ca_certificate_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='CACertificateIdentifier',
        shape_name='String',
    ))

    domain_memberships: DomainMembershipList = _dc.field(metadata=_base.field_metadata(
        member_name='DomainMemberships',
        shape_name='DomainMembershipList',
    ))

    copy_tags_to_snapshot: bool = _dc.field(metadata=_base.field_metadata(
        member_name='CopyTagsToSnapshot',
        shape_name='Boolean',
    ))

    monitoring_interval: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MonitoringInterval',
        shape_name='IntegerOptional',
    ))

    enhanced_monitoring_resource_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='EnhancedMonitoringResourceArn',
        shape_name='String',
    ))

    monitoring_role_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='MonitoringRoleArn',
        shape_name='String',
    ))

    promotion_tier: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='PromotionTier',
        shape_name='IntegerOptional',
    ))

    db_instance_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceArn',
        shape_name='String',
    ))

    timezone: str = _dc.field(metadata=_base.field_metadata(
        member_name='Timezone',
        shape_name='String',
    ))

    iam_database_authentication_enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='IAMDatabaseAuthenticationEnabled',
        shape_name='Boolean',
    ))

    database_insights_mode: DatabaseInsightsMode = _dc.field(metadata=_base.field_metadata(
        member_name='DatabaseInsightsMode',
        shape_name='DatabaseInsightsMode',
    ))

    performance_insights_enabled: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='PerformanceInsightsEnabled',
        shape_name='BooleanOptional',
    ))

    performance_insights_kms_key_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='PerformanceInsightsKMSKeyId',
        shape_name='String',
    ))

    performance_insights_retention_period: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='PerformanceInsightsRetentionPeriod',
        shape_name='IntegerOptional',
    ))

    enabled_cloudwatch_logs_exports: LogTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='EnabledCloudwatchLogsExports',
        shape_name='LogTypeList',
    ))

    processor_features: ProcessorFeatureList = _dc.field(metadata=_base.field_metadata(
        member_name='ProcessorFeatures',
        shape_name='ProcessorFeatureList',
    ))

    deletion_protection: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DeletionProtection',
        shape_name='Boolean',
    ))

    associated_roles: DBInstanceRoles = _dc.field(metadata=_base.field_metadata(
        member_name='AssociatedRoles',
        shape_name='DBInstanceRoles',
    ))

    listener_endpoint: Endpoint = _dc.field(metadata=_base.field_metadata(
        member_name='ListenerEndpoint',
        shape_name='Endpoint',
    ))

    max_allocated_storage: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MaxAllocatedStorage',
        shape_name='IntegerOptional',
    ))

    tag_list: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='TagList',
        shape_name='TagList',
    ))

    db_instance_automated_backups_replications: DBInstanceAutomatedBackupsReplicationList = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstanceAutomatedBackupsReplications',
        shape_name='DBInstanceAutomatedBackupsReplicationList',
    ))

    customer_owned_ip_enabled: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='CustomerOwnedIpEnabled',
        shape_name='BooleanOptional',
    ))

    aws_backup_recovery_point_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='AwsBackupRecoveryPointArn',
        shape_name='String',
    ))

    activity_stream_status: ActivityStreamStatus = _dc.field(metadata=_base.field_metadata(
        member_name='ActivityStreamStatus',
        shape_name='ActivityStreamStatus',
    ))

    activity_stream_kms_key_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='ActivityStreamKmsKeyId',
        shape_name='String',
    ))

    activity_stream_kinesis_stream_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='ActivityStreamKinesisStreamName',
        shape_name='String',
    ))

    activity_stream_mode: ActivityStreamMode = _dc.field(metadata=_base.field_metadata(
        member_name='ActivityStreamMode',
        shape_name='ActivityStreamMode',
    ))

    activity_stream_engine_native_audit_fields_included: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='ActivityStreamEngineNativeAuditFieldsIncluded',
        shape_name='BooleanOptional',
    ))

    automation_mode: AutomationMode = _dc.field(metadata=_base.field_metadata(
        member_name='AutomationMode',
        shape_name='AutomationMode',
    ))

    resume_full_automation_mode_time: TStamp = _dc.field(metadata=_base.field_metadata(
        member_name='ResumeFullAutomationModeTime',
        shape_name='TStamp',
    ))

    custom_iam_instance_profile: str = _dc.field(metadata=_base.field_metadata(
        member_name='CustomIamInstanceProfile',
        shape_name='String',
    ))

    backup_target: str = _dc.field(metadata=_base.field_metadata(
        member_name='BackupTarget',
        shape_name='String',
    ))

    network_type: str = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkType',
        shape_name='String',
    ))

    activity_stream_policy_status: ActivityStreamPolicyStatus = _dc.field(metadata=_base.field_metadata(
        member_name='ActivityStreamPolicyStatus',
        shape_name='ActivityStreamPolicyStatus',
    ))

    storage_throughput: IntegerOptional = _dc.field(metadata=_base.field_metadata(
        member_name='StorageThroughput',
        shape_name='IntegerOptional',
    ))

    db_system_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='DBSystemId',
        shape_name='String',
    ))

    master_user_secret: MasterUserSecret = _dc.field(metadata=_base.field_metadata(
        member_name='MasterUserSecret',
        shape_name='MasterUserSecret',
    ))

    certificate_details: CertificateDetails = _dc.field(metadata=_base.field_metadata(
        member_name='CertificateDetails',
        shape_name='CertificateDetails',
    ))

    read_replica_source_db_cluster_identifier: str = _dc.field(metadata=_base.field_metadata(
        member_name='ReadReplicaSourceDBClusterIdentifier',
        shape_name='String',
    ))

    percent_progress: str = _dc.field(metadata=_base.field_metadata(
        member_name='PercentProgress',
        shape_name='String',
    ))

    dedicated_log_volume: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DedicatedLogVolume',
        shape_name='Boolean',
    ))

    is_storage_config_upgrade_available: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='IsStorageConfigUpgradeAvailable',
        shape_name='BooleanOptional',
    ))

    multi_tenant: BooleanOptional = _dc.field(metadata=_base.field_metadata(
        member_name='MultiTenant',
        shape_name='BooleanOptional',
    ))

    engine_lifecycle_support: str = _dc.field(metadata=_base.field_metadata(
        member_name='EngineLifecycleSupport',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class CreateDBInstanceResult(
    _base.Shape,
    shape_name='CreateDBInstanceResult',
):
    db_instance: DBInstance = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstance',
        shape_name='DBInstance',
    ))


DBInstanceList: _ta.TypeAlias = _ta.Sequence[DBInstance]


@_dc.dataclass(frozen=True)
class DeleteDBInstanceResult(
    _base.Shape,
    shape_name='DeleteDBInstanceResult',
):
    db_instance: DBInstance = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstance',
        shape_name='DBInstance',
    ))


@_dc.dataclass(frozen=True)
class RebootDBInstanceResult(
    _base.Shape,
    shape_name='RebootDBInstanceResult',
):
    db_instance: DBInstance = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstance',
        shape_name='DBInstance',
    ))


@_dc.dataclass(frozen=True)
class StartDBInstanceResult(
    _base.Shape,
    shape_name='StartDBInstanceResult',
):
    db_instance: DBInstance = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstance',
        shape_name='DBInstance',
    ))


@_dc.dataclass(frozen=True)
class StopDBInstanceResult(
    _base.Shape,
    shape_name='StopDBInstanceResult',
):
    db_instance: DBInstance = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstance',
        shape_name='DBInstance',
    ))


@_dc.dataclass(frozen=True)
class DBInstanceMessage(
    _base.Shape,
    shape_name='DBInstanceMessage',
):
    marker: str = _dc.field(metadata=_base.field_metadata(
        member_name='Marker',
        shape_name='String',
    ))

    db_instances: DBInstanceList = _dc.field(metadata=_base.field_metadata(
        member_name='DBInstances',
        shape_name='DBInstanceList',
    ))


ALL_SHAPES: frozenset[type[_base.Shape]] = frozenset([
    AuthorizationNotFoundFault,
    AvailabilityZone,
    BackupPolicyNotFoundFault,
    CertificateDetails,
    CertificateNotFoundFault,
    CreateDBInstanceMessage,
    CreateDBInstanceResult,
    DBClusterNotFoundFault,
    DBInstance,
    DBInstanceAlreadyExistsFault,
    DBInstanceAutomatedBackupQuotaExceededFault,
    DBInstanceAutomatedBackupsReplication,
    DBInstanceMessage,
    DBInstanceNotFoundFault,
    DBInstanceRole,
    DBInstanceStatusInfo,
    DBParameterGroupNotFoundFault,
    DBParameterGroupStatus,
    DBSecurityGroupMembership,
    DBSecurityGroupNotFoundFault,
    DBSnapshotAlreadyExistsFault,
    DBSubnetGroup,
    DBSubnetGroupDoesNotCoverEnoughAZs,
    DBSubnetGroupNotFoundFault,
    DeleteDBInstanceMessage,
    DeleteDBInstanceResult,
    DescribeDBInstancesMessage,
    DomainMembership,
    DomainNotFoundFault,
    Endpoint,
    Filter,
    InstanceQuotaExceededFault,
    InsufficientDBInstanceCapacityFault,
    InvalidDBClusterStateFault,
    InvalidDBInstanceStateFault,
    InvalidSubnet,
    InvalidVPCNetworkStateFault,
    KMSKeyNotAccessibleFault,
    MasterUserSecret,
    NetworkTypeNotSupported,
    OptionGroupMembership,
    OptionGroupNotFoundFault,
    Outpost,
    PendingCloudwatchLogsExports,
    PendingModifiedValues,
    ProcessorFeature,
    ProvisionedIopsNotAvailableInAZFault,
    RebootDBInstanceMessage,
    RebootDBInstanceResult,
    SnapshotQuotaExceededFault,
    StartDBInstanceMessage,
    StartDBInstanceResult,
    StopDBInstanceMessage,
    StopDBInstanceResult,
    StorageQuotaExceededFault,
    StorageTypeNotSupportedFault,
    Subnet,
    TenantDatabaseQuotaExceededFault,
    VpcSecurityGroupMembership,
])


##


CREATE_DB_INSTANCE = _base.Operation(
    name='CreateDBInstance',
    input=CreateDBInstanceMessage,
    output=CreateDBInstanceResult,
    errors=[
        AuthorizationNotFoundFault,
        BackupPolicyNotFoundFault,
        CertificateNotFoundFault,
        DBClusterNotFoundFault,
        DBInstanceAlreadyExistsFault,
        DBParameterGroupNotFoundFault,
        DBSecurityGroupNotFoundFault,
        DBSubnetGroupDoesNotCoverEnoughAZs,
        DBSubnetGroupNotFoundFault,
        DomainNotFoundFault,
        InstanceQuotaExceededFault,
        InsufficientDBInstanceCapacityFault,
        InvalidDBClusterStateFault,
        InvalidSubnet,
        InvalidVPCNetworkStateFault,
        KMSKeyNotAccessibleFault,
        NetworkTypeNotSupported,
        OptionGroupNotFoundFault,
        ProvisionedIopsNotAvailableInAZFault,
        StorageQuotaExceededFault,
        StorageTypeNotSupportedFault,
        TenantDatabaseQuotaExceededFault,
    ],
)

DELETE_DB_INSTANCE = _base.Operation(
    name='DeleteDBInstance',
    input=DeleteDBInstanceMessage,
    output=DeleteDBInstanceResult,
    errors=[
        DBInstanceAutomatedBackupQuotaExceededFault,
        DBInstanceNotFoundFault,
        DBSnapshotAlreadyExistsFault,
        InvalidDBClusterStateFault,
        InvalidDBInstanceStateFault,
        SnapshotQuotaExceededFault,
    ],
)

DESCRIBE_DB_INSTANCES = _base.Operation(
    name='DescribeDBInstances',
    input=DescribeDBInstancesMessage,
    output=DBInstanceMessage,
    errors=[
        DBInstanceNotFoundFault,
    ],
)

REBOOT_DB_INSTANCE = _base.Operation(
    name='RebootDBInstance',
    input=RebootDBInstanceMessage,
    output=RebootDBInstanceResult,
    errors=[
        DBInstanceNotFoundFault,
        InvalidDBInstanceStateFault,
    ],
)

START_DB_INSTANCE = _base.Operation(
    name='StartDBInstance',
    input=StartDBInstanceMessage,
    output=StartDBInstanceResult,
    errors=[
        AuthorizationNotFoundFault,
        DBClusterNotFoundFault,
        DBInstanceNotFoundFault,
        DBSubnetGroupDoesNotCoverEnoughAZs,
        DBSubnetGroupNotFoundFault,
        InsufficientDBInstanceCapacityFault,
        InvalidDBClusterStateFault,
        InvalidDBInstanceStateFault,
        InvalidSubnet,
        InvalidVPCNetworkStateFault,
        KMSKeyNotAccessibleFault,
    ],
)

STOP_DB_INSTANCE = _base.Operation(
    name='StopDBInstance',
    input=StopDBInstanceMessage,
    output=StopDBInstanceResult,
    errors=[
        DBInstanceNotFoundFault,
        DBSnapshotAlreadyExistsFault,
        InvalidDBClusterStateFault,
        InvalidDBInstanceStateFault,
        SnapshotQuotaExceededFault,
    ],
)


ALL_OPERATIONS: frozenset[_base.Operation] = frozenset([
    CREATE_DB_INSTANCE,
    DELETE_DB_INSTANCE,
    DESCRIBE_DB_INSTANCES,
    REBOOT_DB_INSTANCE,
    START_DB_INSTANCE,
    STOP_DB_INSTANCE,
])