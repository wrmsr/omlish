"""
TODO:
 - lb's
 - ebs imgs
 - split compute/network
"""
# import datetime
# import typing as ta
#
# from .base import Model
# from .base import Tags
#
#
# class Image(Model):
#     # architecture: ArchitectureValues
#     creation_date: str
#     image_id: str
#     image_location: str
#     # image_type: ImageTypeValues
#     public: bool
#     kernel_id: str
#     owner_id: str
#     # platform: PlatformValues
#     platform_details: str
#     usage_operation: str
#     # product_codes: ProductCodeList
#     ramdisk_id: str
#     state: str
#     # block_device_mappings: BlockDeviceMappingList
#     description: str
#     ena_support: bool
#     # hypervisor: HypervisorType
#     image_owner_alias: str
#     name: str
#     root_device_name: str
#     # root_device_type: DeviceType
#     sriov_net_support: str
#     state_reason: str
#     tags: Tags = Tags()
#     # virtualization_type: VirtualizationType
#
#
# class VcpuInfo(Model):
#     default_vcpus: int
#     default_cores: int
#     default_threads_per_core: int
#     valid_cores: ta.Sequence[int]
#     valid_threads_per_core: ta.Sequence[int]
#
#
# class MemoryInfo(Model):
#     size_in_mib: int
#
#
# class GpuMemoryInfo(Model):
#     size_in_mib: int
#
#
# class GpuDeviceInfo(Model):
#     name: str
#     manufacturer: str
#     count: int
#     memory_info: GpuMemoryInfo
#
#
# class GpuInfo(Model):
#     gpus: ta.Sequence[GpuDeviceInfo]
#     total_gpu_memory_in_mib: int
#
#
# class InstanceType(Model):
#     instance_type: str
#     # current_generation: CurrentGenerationFlag
#     # free_tier_eligible: FreeTierEligibleFlag
#     # supported_usage_classes: UsageClassTypeList
#     # supported_root_device_types: RootDeviceTypeList
#     # supported_virtualization_types: VirtualizationTypeList
#     # bare_metal: BareMetalFlag
#     # hypervisor: InstanceTypeHypervisor
#     # processor_info: ProcessorInfo
#     vcpu_info: VcpuInfo
#     memory_info: MemoryInfo
#     # instance_storage_supported: InstanceStorageFlag
#     # instance_storage_info: InstanceStorageInfo
#     # ebs_info: EbsInfo
#     # network_info: NetworkInfo
#     gpu_info: GpuInfo
#     # fpga_info: FpgaInfo
#     # placement_group_info: PlacementGroupInfo
#     # inference_accelerator_info: InferenceAcceleratorInfo
#     # hibernation_supported: HibernationFlag
#     # burstable_performance_supported: BurstablePerformanceFlag
#     # dedicated_hosts_supported: DedicatedHostFlag
#     # auto_recovery_supported: AutoRecoveryFlag
#
#
# class InstanceState(Model):
#     code: int
#     name: str
#
#
# class Instance(Model):
#     ami_launch_index: int
#     image_id: str
#     instance_id: str
#     instance_type: str
#     kernel_id: str
#     key_name: str
#     launch_time: datetime.datetime
#     # monitoring: Monitoring
#     # placement: Placement
#     # platform: PlatformValues
#     private_dns_name: str
#     private_ip_address: str
#     # product_codes: ProductCodeList
#     public_dns_name: str
#     public_ip_address: str
#     # ramdisk_id: str
#     state: InstanceState
#     state_transition_reason: str
#     subet_id: str
#     vpc_id: str
#     # architecture: ArchitectureValues
#     # block_device_mappings: InstanceBlockDeviceMappingList
#     client_token: str
#     ebs_optimized: bool
#     ena_support: bool
#     # hypervisor: HypervisorType
#     # iam_instance_profile: IamInstanceProfile
#     # instance_lifecycle: InstanceLifecycleType
#     # elastic_gpu_associations: ElasticGpuAssociationList
#     # elastic_inference_accelerator_associations: ElasticInferenceAcceleratorAssociationList
#     # network_interfaces: InstanceNetworkInterfaceList
#     outpost_arn: str
#     root_device_name: str
#     # root_device_type: DeviceType
#     # security_groups: GroupIdentifierList
#     source_dest_check: bool
#     spot_instance_request_id: str
#     sriov_net_support: str
#     state_reason: str
#     tags: Tags = Tags()
#     # virtualization_type: VirtualizationType
#     # cpu_options: CpuOptions
#     capacity_reservation_id: str
#     # capacity_reservation_specification: CapacityReservationSpecificationResponse
#     # hibernation_options: HibernationOptions
#     # licenses: LicenseList
#     # metadata_options: InstanceMetadataOptionsResponse
#     # enclave_options: EnclaveOptions
#
#
# class KeyPair(Model):
#     key_fingerprint: str
#     # key_material: SensitiveUserData
#     key_name: str
#     key_pair_id: str
#     tags: Tags = Tags()
#
#
# class KeyPairInfo(Model):
#     key_pair_id: str
#     key_fingerprint: str
#     key_name: str
#     tags: Tags = Tags()
#
#
# class IpRange(Model):
#     cidr_ip: str
#     description: str
#
#
# class Ipv6Range(Model):
#     cidr_ipv6: str
#     description: str
#
#
# class IpPermission(Model):
#     from_port: int
#     ip_protocol: str
#     ip_ranges: ta.Sequence[IpRange]
#     ipv6_ranges: ta.Sequence[Ipv6Range]
#     # prefix_list_ids: PrefixListIdList
#     to_port: int
#     # user_id_group_pairs: UserIdGroupPairList
#
#
# class SecurityGroup(Model):
#     description: str
#     group_name: str
#     ip_permissions: ta.Sequence[IpPermission]
#     owner_id: str
#     group_id: str
#     ip_permissions_egress: ta.Sequence[IpPermission]
#     tags: Tags = Tags()
#     vpc_id: str
#
#
# class Vpc(Model):
#     cidr_block: str
#     dhcp_options_id: str
#     # state: VpcState
#     vpc_id: str
#     owner_id: str
#     # instance_tenancy: Tenancy
#     # ipv6_cidr_block_association_set: VpcIpv6CidrBlockAssociationSet
#     # cidr_block_association_set: VpcCidrBlockAssociationSet
#     is_default: bool
#     tags: Tags = Tags()
