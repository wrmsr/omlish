import typing as ta

from .base import Model
from .base import Tags


class DbCluster(Model):
    allocated_storage: ta.Optional[int]
    # availability_zones: AvailabilityZones
    backup_retention_period: ta.Optional[int]
    character_set_name: str
    database_name: str
    db_cluster_identifier: str
    db_cluster_parameter_group: str
    db_subnet_group: str
    status: str
    percent_progress: str
    # earliest_restorable_time: TStamp
    endpoint: str
    reader_endpoint: str
    custom_endpoints: ta.Sequence[str]
    multi_az: ta.Optional[bool]
    engine: str
    engine_version: str
    # latest_restorable_time: TStamp
    port: ta.Optional[int]
    master_username: str
    # db_cluster_option_group_memberships: DbClusterOptionGroupMemberships
    preferred_backup_window: str
    preferred_maintenance_window: str
    replication_source_identifier: str
    # read_replica_identifiers: ReadReplicaIdentifierList
    # db_cluster_members: DbClusterMemberList
    # vpc_security_groups: VpcSecurityGroupMembershipList
    hosted_zone_id: str
    storage_encrypted: bool
    kms_key_id: str
    db_cluster_resource_id: str
    db_cluster_arn: str
    # associated_roles: DbClusterRoles
    iam_database_authentication_enabled: ta.Optional[bool]
    clone_group_id: str
    # cluster_create_time: TStamp
    # earliest_backtrack_time: TStamp
    backtrack_window: ta.Optional[int]
    backtrack_consumed_change_records: ta.Optional[int]
    # enabled_cloudwatch_logs_exports: LogTypeList
    capacity: ta.Optional[int]
    engine_mode: str
    # scaling_configuration_info: ScalingConfigurationInfo
    deletion_protection: ta.Optional[bool]
    http_endpoint_enabled: ta.Optional[bool]
    # activity_stream_mode: ActivityStreamMode
    # activity_stream_status: ActivityStreamStatus
    activity_stream_kms_key_id: str
    activity_stream_kinesis_stream_name: str
    copy_tags_to_snapshot: ta.Optional[bool]
    cross_account_clone: ta.Optional[bool]
    # domain_memberships: DomainMembershipList
    tags: Tags = Tags()
    # global_write_forwarding_status: WriteForwardingStatus
    global_write_forwarding_requested: ta.Optional[bool]
    # pending_modified_values: ClusterPendingModifiedValues


class DbInstance(Model):
    db_instance_identifier: str
    db_instance_class: str
    engine: str
    db_instance_status: str
    master_username: str
    db_name: str
    # endpoint: Endpoint
    allocated_storage: int
    # instance_create_time: TStamp
    preferred_backup_window: str
    backup_retention_period: int
    # db_security_groups: DbSecurityGroupMembershipList
    # vpc_security_groups: VpcSecurityGroupMembershipList
    # db_parameter_groups: DbParameterGroupStatusList
    availability_zone: str
    # db_subnet_group: DbSubnetGroup
    preferred_maintenance_window: str
    # pending_modified_values: PendingModifiedValues
    # latest_restorable_time: TStamp
    multi_az: bool
    engine_version: str
    auto_minor_version_upgrade: bool
    read_replica_source_db_instance_identifier: str
    # read_replica_db_instance_identifiers: ReadReplicaDbInstanceIdentifierList
    # read_replica_db_cluster_identifiers: ReadReplicaDbClusterIdentifierList
    # replica_mode: ReplicaMode
    license_model: str
    iops: ta.Optional[int]
    # option_group_memberships: OptionGroupMembershipList
    character_set_name: str
    nchar_character_set_name: str
    secondary_availability_zone: str
    publicly_accessible: bool
    # status_infos: DbInstanceStatusInfoList
    storage_type: str
    tde_credential_arn: str
    db_instance_port: int
    db_cluster_identifier: str
    storage_encrypted: bool
    kms_key_id: str
    dbi_resource_id: str
    ca_certificate_identifier: str
    # domain_memberships: DomainMembershipList
    copy_tags_to_snapshot: bool
    monitoring_interval: ta.Optional[int]
    enhanced_monitoring_resource_arn: str
    monitoring_role_arn: str
    promotion_tier: ta.Optional[int]
    db_instance_arn: str
    timezone: str
    iam_database_authentication_enabled: bool
    performance_insights_enabled: ta.Optional[bool]
    performance_insights_kmskey_id: str
    performance_insights_retention_period: ta.Optional[int]
    # enabled_cloudwatch_logs_exports: LogTypeList
    # processor_features: ProcessorFeatureList
    deletion_protection: bool
    # associated_roles: DbInstanceRoles
    # listener_endpoint: Endpoint
    max_allocated_storage: ta.Optional[int]
    tags: Tags = Tags()
    # db_instance_automated_backups_replications: DbInstanceAutomatedBackupsReplicationList
    customer_owned_ip_enabled: ta.Optional[bool]
