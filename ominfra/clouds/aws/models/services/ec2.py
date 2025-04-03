# flake8: noqa: E501
# ruff: noqa: N801 S105
# fmt: off
import dataclasses as _dc  # noqa
import enum as _enum  # noqa
import typing as _ta  # noqa

from .. import base as _base  # noqa


##


AllocationId = _ta.NewType('AllocationId', str)


class AmdSevSnpSpecification(_enum.Enum):
    ENABLED = 'enabled'
    DISABLED = 'disabled'


class ArchitectureType(_enum.Enum):
    I386 = 'i386'
    X86_64 = 'x86_64'
    ARM64 = 'arm64'
    X86_64_MAC = 'x86_64_mac'
    ARM64_MAC = 'arm64_mac'


class ArchitectureValues(_enum.Enum):
    I386 = 'i386'
    X86_64 = 'x86_64'
    ARM64 = 'arm64'
    X86_64_MAC = 'x86_64_mac'
    ARM64_MAC = 'arm64_mac'


class AttachmentStatus(_enum.Enum):
    ATTACHING = 'attaching'
    ATTACHED = 'attached'
    DETACHING = 'detaching'
    DETACHED = 'detached'


AutoRecoveryFlag = _ta.NewType('AutoRecoveryFlag', bool)


class BandwidthWeightingType(_enum.Enum):
    DEFAULT = 'default'
    VPC_1 = 'vpc-1'
    EBS_1 = 'ebs-1'


BareMetalFlag = _ta.NewType('BareMetalFlag', bool)

BaselineBandwidthInGbps = _ta.NewType('BaselineBandwidthInGbps', float)

BaselineBandwidthInMbps = _ta.NewType('BaselineBandwidthInMbps', int)

BaselineIops = _ta.NewType('BaselineIops', int)

BaselineThroughputInMBps = _ta.NewType('BaselineThroughputInMBps', float)


class BlockPublicAccessMode(_enum.Enum):
    OFF = 'off'
    BLOCK_BIDIRECTIONAL = 'block-bidirectional'
    BLOCK_INGRESS = 'block-ingress'


class BootModeType(_enum.Enum):
    LEGACY_BIOS = 'legacy-bios'
    UEFI = 'uefi'


class BootModeValues(_enum.Enum):
    LEGACY_BIOS = 'legacy-bios'
    UEFI = 'uefi'
    UEFI_PREFERRED = 'uefi-preferred'


BurstablePerformanceFlag = _ta.NewType('BurstablePerformanceFlag', bool)

CapacityReservationId = _ta.NewType('CapacityReservationId', str)


class CapacityReservationPreference(_enum.Enum):
    CAPACITY_RESERVATIONS_ONLY = 'capacity-reservations-only'
    OPEN = 'open'
    NONE = 'none'


CarrierGatewayId = _ta.NewType('CarrierGatewayId', str)

CoipPoolId = _ta.NewType('CoipPoolId', str)

CoreCount = _ta.NewType('CoreCount', int)

CoreNetworkArn = _ta.NewType('CoreNetworkArn', str)

CpuManufacturerName = _ta.NewType('CpuManufacturerName', str)

CurrentGenerationFlag = _ta.NewType('CurrentGenerationFlag', bool)

DITMaxResults = _ta.NewType('DITMaxResults', int)

DedicatedHostFlag = _ta.NewType('DedicatedHostFlag', bool)

DefaultNetworkCardIndex = _ta.NewType('DefaultNetworkCardIndex', int)

DescribeInternetGatewaysMaxResults = _ta.NewType('DescribeInternetGatewaysMaxResults', int)

DescribeNetworkInterfacesMaxResults = _ta.NewType('DescribeNetworkInterfacesMaxResults', int)

DescribeRouteTablesMaxResults = _ta.NewType('DescribeRouteTablesMaxResults', int)

DescribeSecurityGroupsMaxResults = _ta.NewType('DescribeSecurityGroupsMaxResults', int)

DescribeSubnetsMaxResults = _ta.NewType('DescribeSubnetsMaxResults', int)

DescribeVpcsMaxResults = _ta.NewType('DescribeVpcsMaxResults', int)


class DeviceType(_enum.Enum):
    EBS = 'ebs'
    INSTANCE_STORE = 'instance-store'


DiskCount = _ta.NewType('DiskCount', int)

DiskSize = _ta.NewType('DiskSize', int)


class DiskType(_enum.Enum):
    HDD = 'hdd'
    SSD = 'ssd'


class DomainType(_enum.Enum):
    VPC = 'vpc'
    STANDARD = 'standard'


class EbsEncryptionSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    SUPPORTED = 'supported'


class EbsNvmeSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    SUPPORTED = 'supported'
    REQUIRED = 'required'


class EbsOptimizedSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    SUPPORTED = 'supported'
    DEFAULT = 'default'


EfaSupportedFlag = _ta.NewType('EfaSupportedFlag', bool)

EgressOnlyInternetGatewayId = _ta.NewType('EgressOnlyInternetGatewayId', str)

ElasticGpuId = _ta.NewType('ElasticGpuId', str)

ElasticInferenceAcceleratorCount = _ta.NewType('ElasticInferenceAcceleratorCount', int)

EnaSrdSupported = _ta.NewType('EnaSrdSupported', bool)


class EnaSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    SUPPORTED = 'supported'
    REQUIRED = 'required'


EncryptionInTransitSupported = _ta.NewType('EncryptionInTransitSupported', bool)


class EphemeralNvmeSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    SUPPORTED = 'supported'
    REQUIRED = 'required'


FpgaDeviceCount = _ta.NewType('FpgaDeviceCount', int)

FpgaDeviceManufacturerName = _ta.NewType('FpgaDeviceManufacturerName', str)

FpgaDeviceMemorySize = _ta.NewType('FpgaDeviceMemorySize', int)

FpgaDeviceName = _ta.NewType('FpgaDeviceName', str)

FreeTierEligibleFlag = _ta.NewType('FreeTierEligibleFlag', bool)

GpuDeviceCount = _ta.NewType('GpuDeviceCount', int)

GpuDeviceManufacturerName = _ta.NewType('GpuDeviceManufacturerName', str)

GpuDeviceMemorySize = _ta.NewType('GpuDeviceMemorySize', int)

GpuDeviceName = _ta.NewType('GpuDeviceName', str)

HibernationFlag = _ta.NewType('HibernationFlag', bool)


class HostnameType(_enum.Enum):
    IP_NAME = 'ip-name'
    RESOURCE_NAME = 'resource-name'


class HttpTokensState(_enum.Enum):
    OPTIONAL = 'optional'
    REQUIRED = 'required'


class HypervisorType(_enum.Enum):
    OVM = 'ovm'
    XEN = 'xen'


ImageId = _ta.NewType('ImageId', str)


class ImageState(_enum.Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    INVALID = 'invalid'
    DEREGISTERED = 'deregistered'
    TRANSIENT = 'transient'
    FAILED = 'failed'
    ERROR = 'error'
    DISABLED = 'disabled'


class ImageTypeValues(_enum.Enum):
    MACHINE = 'machine'
    KERNEL = 'kernel'
    RAMDISK = 'ramdisk'


class ImdsSupportValues(_enum.Enum):
    V2_0 = 'v2.0'


InferenceDeviceCount = _ta.NewType('InferenceDeviceCount', int)

InferenceDeviceManufacturerName = _ta.NewType('InferenceDeviceManufacturerName', str)

InferenceDeviceMemorySize = _ta.NewType('InferenceDeviceMemorySize', int)

InferenceDeviceName = _ta.NewType('InferenceDeviceName', str)


class InstanceAutoRecoveryState(_enum.Enum):
    DISABLED = 'disabled'
    DEFAULT = 'default'


class InstanceBandwidthWeighting(_enum.Enum):
    DEFAULT = 'default'
    VPC_1 = 'vpc-1'
    EBS_1 = 'ebs-1'


class InstanceBootModeValues(_enum.Enum):
    LEGACY_BIOS = 'legacy-bios'
    UEFI = 'uefi'


InstanceId = _ta.NewType('InstanceId', str)


class InstanceInterruptionBehavior(_enum.Enum):
    HIBERNATE = 'hibernate'
    STOP = 'stop'
    TERMINATE = 'terminate'


class InstanceLifecycleType(_enum.Enum):
    SPOT = 'spot'
    SCHEDULED = 'scheduled'
    CAPACITY_BLOCK = 'capacity-block'


class InstanceMetadataEndpointState(_enum.Enum):
    DISABLED = 'disabled'
    ENABLED = 'enabled'


class InstanceMetadataOptionsState(_enum.Enum):
    PENDING = 'pending'
    APPLIED = 'applied'


class InstanceMetadataProtocolState(_enum.Enum):
    DISABLED = 'disabled'
    ENABLED = 'enabled'


class InstanceMetadataTagsState(_enum.Enum):
    DISABLED = 'disabled'
    ENABLED = 'enabled'


class InstanceStateName(_enum.Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SHUTTING_DOWN = 'shutting-down'
    TERMINATED = 'terminated'
    STOPPING = 'stopping'
    STOPPED = 'stopped'


class InstanceStorageEncryptionSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    REQUIRED = 'required'


InstanceStorageFlag = _ta.NewType('InstanceStorageFlag', bool)


class InstanceType(_enum.Enum):
    A1_MEDIUM = 'a1.medium'
    A1_LARGE = 'a1.large'
    A1_XLARGE = 'a1.xlarge'
    A1_2XLARGE = 'a1.2xlarge'
    A1_4XLARGE = 'a1.4xlarge'
    A1_METAL = 'a1.metal'
    C1_MEDIUM = 'c1.medium'
    C1_XLARGE = 'c1.xlarge'
    C3_LARGE = 'c3.large'
    C3_XLARGE = 'c3.xlarge'
    C3_2XLARGE = 'c3.2xlarge'
    C3_4XLARGE = 'c3.4xlarge'
    C3_8XLARGE = 'c3.8xlarge'
    C4_LARGE = 'c4.large'
    C4_XLARGE = 'c4.xlarge'
    C4_2XLARGE = 'c4.2xlarge'
    C4_4XLARGE = 'c4.4xlarge'
    C4_8XLARGE = 'c4.8xlarge'
    C5_LARGE = 'c5.large'
    C5_XLARGE = 'c5.xlarge'
    C5_2XLARGE = 'c5.2xlarge'
    C5_4XLARGE = 'c5.4xlarge'
    C5_9XLARGE = 'c5.9xlarge'
    C5_12XLARGE = 'c5.12xlarge'
    C5_18XLARGE = 'c5.18xlarge'
    C5_24XLARGE = 'c5.24xlarge'
    C5_METAL = 'c5.metal'
    C5A_LARGE = 'c5a.large'
    C5A_XLARGE = 'c5a.xlarge'
    C5A_2XLARGE = 'c5a.2xlarge'
    C5A_4XLARGE = 'c5a.4xlarge'
    C5A_8XLARGE = 'c5a.8xlarge'
    C5A_12XLARGE = 'c5a.12xlarge'
    C5A_16XLARGE = 'c5a.16xlarge'
    C5A_24XLARGE = 'c5a.24xlarge'
    C5AD_LARGE = 'c5ad.large'
    C5AD_XLARGE = 'c5ad.xlarge'
    C5AD_2XLARGE = 'c5ad.2xlarge'
    C5AD_4XLARGE = 'c5ad.4xlarge'
    C5AD_8XLARGE = 'c5ad.8xlarge'
    C5AD_12XLARGE = 'c5ad.12xlarge'
    C5AD_16XLARGE = 'c5ad.16xlarge'
    C5AD_24XLARGE = 'c5ad.24xlarge'
    C5D_LARGE = 'c5d.large'
    C5D_XLARGE = 'c5d.xlarge'
    C5D_2XLARGE = 'c5d.2xlarge'
    C5D_4XLARGE = 'c5d.4xlarge'
    C5D_9XLARGE = 'c5d.9xlarge'
    C5D_12XLARGE = 'c5d.12xlarge'
    C5D_18XLARGE = 'c5d.18xlarge'
    C5D_24XLARGE = 'c5d.24xlarge'
    C5D_METAL = 'c5d.metal'
    C5N_LARGE = 'c5n.large'
    C5N_XLARGE = 'c5n.xlarge'
    C5N_2XLARGE = 'c5n.2xlarge'
    C5N_4XLARGE = 'c5n.4xlarge'
    C5N_9XLARGE = 'c5n.9xlarge'
    C5N_18XLARGE = 'c5n.18xlarge'
    C5N_METAL = 'c5n.metal'
    C6G_MEDIUM = 'c6g.medium'
    C6G_LARGE = 'c6g.large'
    C6G_XLARGE = 'c6g.xlarge'
    C6G_2XLARGE = 'c6g.2xlarge'
    C6G_4XLARGE = 'c6g.4xlarge'
    C6G_8XLARGE = 'c6g.8xlarge'
    C6G_12XLARGE = 'c6g.12xlarge'
    C6G_16XLARGE = 'c6g.16xlarge'
    C6G_METAL = 'c6g.metal'
    C6GD_MEDIUM = 'c6gd.medium'
    C6GD_LARGE = 'c6gd.large'
    C6GD_XLARGE = 'c6gd.xlarge'
    C6GD_2XLARGE = 'c6gd.2xlarge'
    C6GD_4XLARGE = 'c6gd.4xlarge'
    C6GD_8XLARGE = 'c6gd.8xlarge'
    C6GD_12XLARGE = 'c6gd.12xlarge'
    C6GD_16XLARGE = 'c6gd.16xlarge'
    C6GD_METAL = 'c6gd.metal'
    C6GN_MEDIUM = 'c6gn.medium'
    C6GN_LARGE = 'c6gn.large'
    C6GN_XLARGE = 'c6gn.xlarge'
    C6GN_2XLARGE = 'c6gn.2xlarge'
    C6GN_4XLARGE = 'c6gn.4xlarge'
    C6GN_8XLARGE = 'c6gn.8xlarge'
    C6GN_12XLARGE = 'c6gn.12xlarge'
    C6GN_16XLARGE = 'c6gn.16xlarge'
    C6I_LARGE = 'c6i.large'
    C6I_XLARGE = 'c6i.xlarge'
    C6I_2XLARGE = 'c6i.2xlarge'
    C6I_4XLARGE = 'c6i.4xlarge'
    C6I_8XLARGE = 'c6i.8xlarge'
    C6I_12XLARGE = 'c6i.12xlarge'
    C6I_16XLARGE = 'c6i.16xlarge'
    C6I_24XLARGE = 'c6i.24xlarge'
    C6I_32XLARGE = 'c6i.32xlarge'
    C6I_METAL = 'c6i.metal'
    CC1_4XLARGE = 'cc1.4xlarge'
    CC2_8XLARGE = 'cc2.8xlarge'
    CG1_4XLARGE = 'cg1.4xlarge'
    CR1_8XLARGE = 'cr1.8xlarge'
    D2_XLARGE = 'd2.xlarge'
    D2_2XLARGE = 'd2.2xlarge'
    D2_4XLARGE = 'd2.4xlarge'
    D2_8XLARGE = 'd2.8xlarge'
    D3_XLARGE = 'd3.xlarge'
    D3_2XLARGE = 'd3.2xlarge'
    D3_4XLARGE = 'd3.4xlarge'
    D3_8XLARGE = 'd3.8xlarge'
    D3EN_XLARGE = 'd3en.xlarge'
    D3EN_2XLARGE = 'd3en.2xlarge'
    D3EN_4XLARGE = 'd3en.4xlarge'
    D3EN_6XLARGE = 'd3en.6xlarge'
    D3EN_8XLARGE = 'd3en.8xlarge'
    D3EN_12XLARGE = 'd3en.12xlarge'
    DL1_24XLARGE = 'dl1.24xlarge'
    F1_2XLARGE = 'f1.2xlarge'
    F1_4XLARGE = 'f1.4xlarge'
    F1_16XLARGE = 'f1.16xlarge'
    G2_2XLARGE = 'g2.2xlarge'
    G2_8XLARGE = 'g2.8xlarge'
    G3_4XLARGE = 'g3.4xlarge'
    G3_8XLARGE = 'g3.8xlarge'
    G3_16XLARGE = 'g3.16xlarge'
    G3S_XLARGE = 'g3s.xlarge'
    G4AD_XLARGE = 'g4ad.xlarge'
    G4AD_2XLARGE = 'g4ad.2xlarge'
    G4AD_4XLARGE = 'g4ad.4xlarge'
    G4AD_8XLARGE = 'g4ad.8xlarge'
    G4AD_16XLARGE = 'g4ad.16xlarge'
    G4DN_XLARGE = 'g4dn.xlarge'
    G4DN_2XLARGE = 'g4dn.2xlarge'
    G4DN_4XLARGE = 'g4dn.4xlarge'
    G4DN_8XLARGE = 'g4dn.8xlarge'
    G4DN_12XLARGE = 'g4dn.12xlarge'
    G4DN_16XLARGE = 'g4dn.16xlarge'
    G4DN_METAL = 'g4dn.metal'
    G5_XLARGE = 'g5.xlarge'
    G5_2XLARGE = 'g5.2xlarge'
    G5_4XLARGE = 'g5.4xlarge'
    G5_8XLARGE = 'g5.8xlarge'
    G5_12XLARGE = 'g5.12xlarge'
    G5_16XLARGE = 'g5.16xlarge'
    G5_24XLARGE = 'g5.24xlarge'
    G5_48XLARGE = 'g5.48xlarge'
    G5G_XLARGE = 'g5g.xlarge'
    G5G_2XLARGE = 'g5g.2xlarge'
    G5G_4XLARGE = 'g5g.4xlarge'
    G5G_8XLARGE = 'g5g.8xlarge'
    G5G_16XLARGE = 'g5g.16xlarge'
    G5G_METAL = 'g5g.metal'
    HI1_4XLARGE = 'hi1.4xlarge'
    HPC6A_48XLARGE = 'hpc6a.48xlarge'
    HS1_8XLARGE = 'hs1.8xlarge'
    H1_2XLARGE = 'h1.2xlarge'
    H1_4XLARGE = 'h1.4xlarge'
    H1_8XLARGE = 'h1.8xlarge'
    H1_16XLARGE = 'h1.16xlarge'
    I2_XLARGE = 'i2.xlarge'
    I2_2XLARGE = 'i2.2xlarge'
    I2_4XLARGE = 'i2.4xlarge'
    I2_8XLARGE = 'i2.8xlarge'
    I3_LARGE = 'i3.large'
    I3_XLARGE = 'i3.xlarge'
    I3_2XLARGE = 'i3.2xlarge'
    I3_4XLARGE = 'i3.4xlarge'
    I3_8XLARGE = 'i3.8xlarge'
    I3_16XLARGE = 'i3.16xlarge'
    I3_METAL = 'i3.metal'
    I3EN_LARGE = 'i3en.large'
    I3EN_XLARGE = 'i3en.xlarge'
    I3EN_2XLARGE = 'i3en.2xlarge'
    I3EN_3XLARGE = 'i3en.3xlarge'
    I3EN_6XLARGE = 'i3en.6xlarge'
    I3EN_12XLARGE = 'i3en.12xlarge'
    I3EN_24XLARGE = 'i3en.24xlarge'
    I3EN_METAL = 'i3en.metal'
    IM4GN_LARGE = 'im4gn.large'
    IM4GN_XLARGE = 'im4gn.xlarge'
    IM4GN_2XLARGE = 'im4gn.2xlarge'
    IM4GN_4XLARGE = 'im4gn.4xlarge'
    IM4GN_8XLARGE = 'im4gn.8xlarge'
    IM4GN_16XLARGE = 'im4gn.16xlarge'
    INF1_XLARGE = 'inf1.xlarge'
    INF1_2XLARGE = 'inf1.2xlarge'
    INF1_6XLARGE = 'inf1.6xlarge'
    INF1_24XLARGE = 'inf1.24xlarge'
    IS4GEN_MEDIUM = 'is4gen.medium'
    IS4GEN_LARGE = 'is4gen.large'
    IS4GEN_XLARGE = 'is4gen.xlarge'
    IS4GEN_2XLARGE = 'is4gen.2xlarge'
    IS4GEN_4XLARGE = 'is4gen.4xlarge'
    IS4GEN_8XLARGE = 'is4gen.8xlarge'
    M1_SMALL = 'm1.small'
    M1_MEDIUM = 'm1.medium'
    M1_LARGE = 'm1.large'
    M1_XLARGE = 'm1.xlarge'
    M2_XLARGE = 'm2.xlarge'
    M2_2XLARGE = 'm2.2xlarge'
    M2_4XLARGE = 'm2.4xlarge'
    M3_MEDIUM = 'm3.medium'
    M3_LARGE = 'm3.large'
    M3_XLARGE = 'm3.xlarge'
    M3_2XLARGE = 'm3.2xlarge'
    M4_LARGE = 'm4.large'
    M4_XLARGE = 'm4.xlarge'
    M4_2XLARGE = 'm4.2xlarge'
    M4_4XLARGE = 'm4.4xlarge'
    M4_10XLARGE = 'm4.10xlarge'
    M4_16XLARGE = 'm4.16xlarge'
    M5_LARGE = 'm5.large'
    M5_XLARGE = 'm5.xlarge'
    M5_2XLARGE = 'm5.2xlarge'
    M5_4XLARGE = 'm5.4xlarge'
    M5_8XLARGE = 'm5.8xlarge'
    M5_12XLARGE = 'm5.12xlarge'
    M5_16XLARGE = 'm5.16xlarge'
    M5_24XLARGE = 'm5.24xlarge'
    M5_METAL = 'm5.metal'
    M5A_LARGE = 'm5a.large'
    M5A_XLARGE = 'm5a.xlarge'
    M5A_2XLARGE = 'm5a.2xlarge'
    M5A_4XLARGE = 'm5a.4xlarge'
    M5A_8XLARGE = 'm5a.8xlarge'
    M5A_12XLARGE = 'm5a.12xlarge'
    M5A_16XLARGE = 'm5a.16xlarge'
    M5A_24XLARGE = 'm5a.24xlarge'
    M5AD_LARGE = 'm5ad.large'
    M5AD_XLARGE = 'm5ad.xlarge'
    M5AD_2XLARGE = 'm5ad.2xlarge'
    M5AD_4XLARGE = 'm5ad.4xlarge'
    M5AD_8XLARGE = 'm5ad.8xlarge'
    M5AD_12XLARGE = 'm5ad.12xlarge'
    M5AD_16XLARGE = 'm5ad.16xlarge'
    M5AD_24XLARGE = 'm5ad.24xlarge'
    M5D_LARGE = 'm5d.large'
    M5D_XLARGE = 'm5d.xlarge'
    M5D_2XLARGE = 'm5d.2xlarge'
    M5D_4XLARGE = 'm5d.4xlarge'
    M5D_8XLARGE = 'm5d.8xlarge'
    M5D_12XLARGE = 'm5d.12xlarge'
    M5D_16XLARGE = 'm5d.16xlarge'
    M5D_24XLARGE = 'm5d.24xlarge'
    M5D_METAL = 'm5d.metal'
    M5DN_LARGE = 'm5dn.large'
    M5DN_XLARGE = 'm5dn.xlarge'
    M5DN_2XLARGE = 'm5dn.2xlarge'
    M5DN_4XLARGE = 'm5dn.4xlarge'
    M5DN_8XLARGE = 'm5dn.8xlarge'
    M5DN_12XLARGE = 'm5dn.12xlarge'
    M5DN_16XLARGE = 'm5dn.16xlarge'
    M5DN_24XLARGE = 'm5dn.24xlarge'
    M5DN_METAL = 'm5dn.metal'
    M5N_LARGE = 'm5n.large'
    M5N_XLARGE = 'm5n.xlarge'
    M5N_2XLARGE = 'm5n.2xlarge'
    M5N_4XLARGE = 'm5n.4xlarge'
    M5N_8XLARGE = 'm5n.8xlarge'
    M5N_12XLARGE = 'm5n.12xlarge'
    M5N_16XLARGE = 'm5n.16xlarge'
    M5N_24XLARGE = 'm5n.24xlarge'
    M5N_METAL = 'm5n.metal'
    M5ZN_LARGE = 'm5zn.large'
    M5ZN_XLARGE = 'm5zn.xlarge'
    M5ZN_2XLARGE = 'm5zn.2xlarge'
    M5ZN_3XLARGE = 'm5zn.3xlarge'
    M5ZN_6XLARGE = 'm5zn.6xlarge'
    M5ZN_12XLARGE = 'm5zn.12xlarge'
    M5ZN_METAL = 'm5zn.metal'
    M6A_LARGE = 'm6a.large'
    M6A_XLARGE = 'm6a.xlarge'
    M6A_2XLARGE = 'm6a.2xlarge'
    M6A_4XLARGE = 'm6a.4xlarge'
    M6A_8XLARGE = 'm6a.8xlarge'
    M6A_12XLARGE = 'm6a.12xlarge'
    M6A_16XLARGE = 'm6a.16xlarge'
    M6A_24XLARGE = 'm6a.24xlarge'
    M6A_32XLARGE = 'm6a.32xlarge'
    M6A_48XLARGE = 'm6a.48xlarge'
    M6G_METAL = 'm6g.metal'
    M6G_MEDIUM = 'm6g.medium'
    M6G_LARGE = 'm6g.large'
    M6G_XLARGE = 'm6g.xlarge'
    M6G_2XLARGE = 'm6g.2xlarge'
    M6G_4XLARGE = 'm6g.4xlarge'
    M6G_8XLARGE = 'm6g.8xlarge'
    M6G_12XLARGE = 'm6g.12xlarge'
    M6G_16XLARGE = 'm6g.16xlarge'
    M6GD_METAL = 'm6gd.metal'
    M6GD_MEDIUM = 'm6gd.medium'
    M6GD_LARGE = 'm6gd.large'
    M6GD_XLARGE = 'm6gd.xlarge'
    M6GD_2XLARGE = 'm6gd.2xlarge'
    M6GD_4XLARGE = 'm6gd.4xlarge'
    M6GD_8XLARGE = 'm6gd.8xlarge'
    M6GD_12XLARGE = 'm6gd.12xlarge'
    M6GD_16XLARGE = 'm6gd.16xlarge'
    M6I_LARGE = 'm6i.large'
    M6I_XLARGE = 'm6i.xlarge'
    M6I_2XLARGE = 'm6i.2xlarge'
    M6I_4XLARGE = 'm6i.4xlarge'
    M6I_8XLARGE = 'm6i.8xlarge'
    M6I_12XLARGE = 'm6i.12xlarge'
    M6I_16XLARGE = 'm6i.16xlarge'
    M6I_24XLARGE = 'm6i.24xlarge'
    M6I_32XLARGE = 'm6i.32xlarge'
    M6I_METAL = 'm6i.metal'
    MAC1_METAL = 'mac1.metal'
    P2_XLARGE = 'p2.xlarge'
    P2_8XLARGE = 'p2.8xlarge'
    P2_16XLARGE = 'p2.16xlarge'
    P3_2XLARGE = 'p3.2xlarge'
    P3_8XLARGE = 'p3.8xlarge'
    P3_16XLARGE = 'p3.16xlarge'
    P3DN_24XLARGE = 'p3dn.24xlarge'
    P4D_24XLARGE = 'p4d.24xlarge'
    R3_LARGE = 'r3.large'
    R3_XLARGE = 'r3.xlarge'
    R3_2XLARGE = 'r3.2xlarge'
    R3_4XLARGE = 'r3.4xlarge'
    R3_8XLARGE = 'r3.8xlarge'
    R4_LARGE = 'r4.large'
    R4_XLARGE = 'r4.xlarge'
    R4_2XLARGE = 'r4.2xlarge'
    R4_4XLARGE = 'r4.4xlarge'
    R4_8XLARGE = 'r4.8xlarge'
    R4_16XLARGE = 'r4.16xlarge'
    R5_LARGE = 'r5.large'
    R5_XLARGE = 'r5.xlarge'
    R5_2XLARGE = 'r5.2xlarge'
    R5_4XLARGE = 'r5.4xlarge'
    R5_8XLARGE = 'r5.8xlarge'
    R5_12XLARGE = 'r5.12xlarge'
    R5_16XLARGE = 'r5.16xlarge'
    R5_24XLARGE = 'r5.24xlarge'
    R5_METAL = 'r5.metal'
    R5A_LARGE = 'r5a.large'
    R5A_XLARGE = 'r5a.xlarge'
    R5A_2XLARGE = 'r5a.2xlarge'
    R5A_4XLARGE = 'r5a.4xlarge'
    R5A_8XLARGE = 'r5a.8xlarge'
    R5A_12XLARGE = 'r5a.12xlarge'
    R5A_16XLARGE = 'r5a.16xlarge'
    R5A_24XLARGE = 'r5a.24xlarge'
    R5AD_LARGE = 'r5ad.large'
    R5AD_XLARGE = 'r5ad.xlarge'
    R5AD_2XLARGE = 'r5ad.2xlarge'
    R5AD_4XLARGE = 'r5ad.4xlarge'
    R5AD_8XLARGE = 'r5ad.8xlarge'
    R5AD_12XLARGE = 'r5ad.12xlarge'
    R5AD_16XLARGE = 'r5ad.16xlarge'
    R5AD_24XLARGE = 'r5ad.24xlarge'
    R5B_LARGE = 'r5b.large'
    R5B_XLARGE = 'r5b.xlarge'
    R5B_2XLARGE = 'r5b.2xlarge'
    R5B_4XLARGE = 'r5b.4xlarge'
    R5B_8XLARGE = 'r5b.8xlarge'
    R5B_12XLARGE = 'r5b.12xlarge'
    R5B_16XLARGE = 'r5b.16xlarge'
    R5B_24XLARGE = 'r5b.24xlarge'
    R5B_METAL = 'r5b.metal'
    R5D_LARGE = 'r5d.large'
    R5D_XLARGE = 'r5d.xlarge'
    R5D_2XLARGE = 'r5d.2xlarge'
    R5D_4XLARGE = 'r5d.4xlarge'
    R5D_8XLARGE = 'r5d.8xlarge'
    R5D_12XLARGE = 'r5d.12xlarge'
    R5D_16XLARGE = 'r5d.16xlarge'
    R5D_24XLARGE = 'r5d.24xlarge'
    R5D_METAL = 'r5d.metal'
    R5DN_LARGE = 'r5dn.large'
    R5DN_XLARGE = 'r5dn.xlarge'
    R5DN_2XLARGE = 'r5dn.2xlarge'
    R5DN_4XLARGE = 'r5dn.4xlarge'
    R5DN_8XLARGE = 'r5dn.8xlarge'
    R5DN_12XLARGE = 'r5dn.12xlarge'
    R5DN_16XLARGE = 'r5dn.16xlarge'
    R5DN_24XLARGE = 'r5dn.24xlarge'
    R5DN_METAL = 'r5dn.metal'
    R5N_LARGE = 'r5n.large'
    R5N_XLARGE = 'r5n.xlarge'
    R5N_2XLARGE = 'r5n.2xlarge'
    R5N_4XLARGE = 'r5n.4xlarge'
    R5N_8XLARGE = 'r5n.8xlarge'
    R5N_12XLARGE = 'r5n.12xlarge'
    R5N_16XLARGE = 'r5n.16xlarge'
    R5N_24XLARGE = 'r5n.24xlarge'
    R5N_METAL = 'r5n.metal'
    R6G_MEDIUM = 'r6g.medium'
    R6G_LARGE = 'r6g.large'
    R6G_XLARGE = 'r6g.xlarge'
    R6G_2XLARGE = 'r6g.2xlarge'
    R6G_4XLARGE = 'r6g.4xlarge'
    R6G_8XLARGE = 'r6g.8xlarge'
    R6G_12XLARGE = 'r6g.12xlarge'
    R6G_16XLARGE = 'r6g.16xlarge'
    R6G_METAL = 'r6g.metal'
    R6GD_MEDIUM = 'r6gd.medium'
    R6GD_LARGE = 'r6gd.large'
    R6GD_XLARGE = 'r6gd.xlarge'
    R6GD_2XLARGE = 'r6gd.2xlarge'
    R6GD_4XLARGE = 'r6gd.4xlarge'
    R6GD_8XLARGE = 'r6gd.8xlarge'
    R6GD_12XLARGE = 'r6gd.12xlarge'
    R6GD_16XLARGE = 'r6gd.16xlarge'
    R6GD_METAL = 'r6gd.metal'
    R6I_LARGE = 'r6i.large'
    R6I_XLARGE = 'r6i.xlarge'
    R6I_2XLARGE = 'r6i.2xlarge'
    R6I_4XLARGE = 'r6i.4xlarge'
    R6I_8XLARGE = 'r6i.8xlarge'
    R6I_12XLARGE = 'r6i.12xlarge'
    R6I_16XLARGE = 'r6i.16xlarge'
    R6I_24XLARGE = 'r6i.24xlarge'
    R6I_32XLARGE = 'r6i.32xlarge'
    R6I_METAL = 'r6i.metal'
    T1_MICRO = 't1.micro'
    T2_NANO = 't2.nano'
    T2_MICRO = 't2.micro'
    T2_SMALL = 't2.small'
    T2_MEDIUM = 't2.medium'
    T2_LARGE = 't2.large'
    T2_XLARGE = 't2.xlarge'
    T2_2XLARGE = 't2.2xlarge'
    T3_NANO = 't3.nano'
    T3_MICRO = 't3.micro'
    T3_SMALL = 't3.small'
    T3_MEDIUM = 't3.medium'
    T3_LARGE = 't3.large'
    T3_XLARGE = 't3.xlarge'
    T3_2XLARGE = 't3.2xlarge'
    T3A_NANO = 't3a.nano'
    T3A_MICRO = 't3a.micro'
    T3A_SMALL = 't3a.small'
    T3A_MEDIUM = 't3a.medium'
    T3A_LARGE = 't3a.large'
    T3A_XLARGE = 't3a.xlarge'
    T3A_2XLARGE = 't3a.2xlarge'
    T4G_NANO = 't4g.nano'
    T4G_MICRO = 't4g.micro'
    T4G_SMALL = 't4g.small'
    T4G_MEDIUM = 't4g.medium'
    T4G_LARGE = 't4g.large'
    T4G_XLARGE = 't4g.xlarge'
    T4G_2XLARGE = 't4g.2xlarge'
    U_6TB1_56XLARGE = 'u-6tb1.56xlarge'
    U_6TB1_112XLARGE = 'u-6tb1.112xlarge'
    U_9TB1_112XLARGE = 'u-9tb1.112xlarge'
    U_12TB1_112XLARGE = 'u-12tb1.112xlarge'
    U_6TB1_METAL = 'u-6tb1.metal'
    U_9TB1_METAL = 'u-9tb1.metal'
    U_12TB1_METAL = 'u-12tb1.metal'
    U_18TB1_METAL = 'u-18tb1.metal'
    U_24TB1_METAL = 'u-24tb1.metal'
    VT1_3XLARGE = 'vt1.3xlarge'
    VT1_6XLARGE = 'vt1.6xlarge'
    VT1_24XLARGE = 'vt1.24xlarge'
    X1_16XLARGE = 'x1.16xlarge'
    X1_32XLARGE = 'x1.32xlarge'
    X1E_XLARGE = 'x1e.xlarge'
    X1E_2XLARGE = 'x1e.2xlarge'
    X1E_4XLARGE = 'x1e.4xlarge'
    X1E_8XLARGE = 'x1e.8xlarge'
    X1E_16XLARGE = 'x1e.16xlarge'
    X1E_32XLARGE = 'x1e.32xlarge'
    X2IEZN_2XLARGE = 'x2iezn.2xlarge'
    X2IEZN_4XLARGE = 'x2iezn.4xlarge'
    X2IEZN_6XLARGE = 'x2iezn.6xlarge'
    X2IEZN_8XLARGE = 'x2iezn.8xlarge'
    X2IEZN_12XLARGE = 'x2iezn.12xlarge'
    X2IEZN_METAL = 'x2iezn.metal'
    X2GD_MEDIUM = 'x2gd.medium'
    X2GD_LARGE = 'x2gd.large'
    X2GD_XLARGE = 'x2gd.xlarge'
    X2GD_2XLARGE = 'x2gd.2xlarge'
    X2GD_4XLARGE = 'x2gd.4xlarge'
    X2GD_8XLARGE = 'x2gd.8xlarge'
    X2GD_12XLARGE = 'x2gd.12xlarge'
    X2GD_16XLARGE = 'x2gd.16xlarge'
    X2GD_METAL = 'x2gd.metal'
    Z1D_LARGE = 'z1d.large'
    Z1D_XLARGE = 'z1d.xlarge'
    Z1D_2XLARGE = 'z1d.2xlarge'
    Z1D_3XLARGE = 'z1d.3xlarge'
    Z1D_6XLARGE = 'z1d.6xlarge'
    Z1D_12XLARGE = 'z1d.12xlarge'
    Z1D_METAL = 'z1d.metal'
    X2IDN_16XLARGE = 'x2idn.16xlarge'
    X2IDN_24XLARGE = 'x2idn.24xlarge'
    X2IDN_32XLARGE = 'x2idn.32xlarge'
    X2IEDN_XLARGE = 'x2iedn.xlarge'
    X2IEDN_2XLARGE = 'x2iedn.2xlarge'
    X2IEDN_4XLARGE = 'x2iedn.4xlarge'
    X2IEDN_8XLARGE = 'x2iedn.8xlarge'
    X2IEDN_16XLARGE = 'x2iedn.16xlarge'
    X2IEDN_24XLARGE = 'x2iedn.24xlarge'
    X2IEDN_32XLARGE = 'x2iedn.32xlarge'
    C6A_LARGE = 'c6a.large'
    C6A_XLARGE = 'c6a.xlarge'
    C6A_2XLARGE = 'c6a.2xlarge'
    C6A_4XLARGE = 'c6a.4xlarge'
    C6A_8XLARGE = 'c6a.8xlarge'
    C6A_12XLARGE = 'c6a.12xlarge'
    C6A_16XLARGE = 'c6a.16xlarge'
    C6A_24XLARGE = 'c6a.24xlarge'
    C6A_32XLARGE = 'c6a.32xlarge'
    C6A_48XLARGE = 'c6a.48xlarge'
    C6A_METAL = 'c6a.metal'
    M6A_METAL = 'm6a.metal'
    I4I_LARGE = 'i4i.large'
    I4I_XLARGE = 'i4i.xlarge'
    I4I_2XLARGE = 'i4i.2xlarge'
    I4I_4XLARGE = 'i4i.4xlarge'
    I4I_8XLARGE = 'i4i.8xlarge'
    I4I_16XLARGE = 'i4i.16xlarge'
    I4I_32XLARGE = 'i4i.32xlarge'
    I4I_METAL = 'i4i.metal'
    X2IDN_METAL = 'x2idn.metal'
    X2IEDN_METAL = 'x2iedn.metal'
    C7G_MEDIUM = 'c7g.medium'
    C7G_LARGE = 'c7g.large'
    C7G_XLARGE = 'c7g.xlarge'
    C7G_2XLARGE = 'c7g.2xlarge'
    C7G_4XLARGE = 'c7g.4xlarge'
    C7G_8XLARGE = 'c7g.8xlarge'
    C7G_12XLARGE = 'c7g.12xlarge'
    C7G_16XLARGE = 'c7g.16xlarge'
    MAC2_METAL = 'mac2.metal'
    C6ID_LARGE = 'c6id.large'
    C6ID_XLARGE = 'c6id.xlarge'
    C6ID_2XLARGE = 'c6id.2xlarge'
    C6ID_4XLARGE = 'c6id.4xlarge'
    C6ID_8XLARGE = 'c6id.8xlarge'
    C6ID_12XLARGE = 'c6id.12xlarge'
    C6ID_16XLARGE = 'c6id.16xlarge'
    C6ID_24XLARGE = 'c6id.24xlarge'
    C6ID_32XLARGE = 'c6id.32xlarge'
    C6ID_METAL = 'c6id.metal'
    M6ID_LARGE = 'm6id.large'
    M6ID_XLARGE = 'm6id.xlarge'
    M6ID_2XLARGE = 'm6id.2xlarge'
    M6ID_4XLARGE = 'm6id.4xlarge'
    M6ID_8XLARGE = 'm6id.8xlarge'
    M6ID_12XLARGE = 'm6id.12xlarge'
    M6ID_16XLARGE = 'm6id.16xlarge'
    M6ID_24XLARGE = 'm6id.24xlarge'
    M6ID_32XLARGE = 'm6id.32xlarge'
    M6ID_METAL = 'm6id.metal'
    R6ID_LARGE = 'r6id.large'
    R6ID_XLARGE = 'r6id.xlarge'
    R6ID_2XLARGE = 'r6id.2xlarge'
    R6ID_4XLARGE = 'r6id.4xlarge'
    R6ID_8XLARGE = 'r6id.8xlarge'
    R6ID_12XLARGE = 'r6id.12xlarge'
    R6ID_16XLARGE = 'r6id.16xlarge'
    R6ID_24XLARGE = 'r6id.24xlarge'
    R6ID_32XLARGE = 'r6id.32xlarge'
    R6ID_METAL = 'r6id.metal'
    R6A_LARGE = 'r6a.large'
    R6A_XLARGE = 'r6a.xlarge'
    R6A_2XLARGE = 'r6a.2xlarge'
    R6A_4XLARGE = 'r6a.4xlarge'
    R6A_8XLARGE = 'r6a.8xlarge'
    R6A_12XLARGE = 'r6a.12xlarge'
    R6A_16XLARGE = 'r6a.16xlarge'
    R6A_24XLARGE = 'r6a.24xlarge'
    R6A_32XLARGE = 'r6a.32xlarge'
    R6A_48XLARGE = 'r6a.48xlarge'
    R6A_METAL = 'r6a.metal'
    P4DE_24XLARGE = 'p4de.24xlarge'
    U_3TB1_56XLARGE = 'u-3tb1.56xlarge'
    U_18TB1_112XLARGE = 'u-18tb1.112xlarge'
    U_24TB1_112XLARGE = 'u-24tb1.112xlarge'
    TRN1_2XLARGE = 'trn1.2xlarge'
    TRN1_32XLARGE = 'trn1.32xlarge'
    HPC6ID_32XLARGE = 'hpc6id.32xlarge'
    C6IN_LARGE = 'c6in.large'
    C6IN_XLARGE = 'c6in.xlarge'
    C6IN_2XLARGE = 'c6in.2xlarge'
    C6IN_4XLARGE = 'c6in.4xlarge'
    C6IN_8XLARGE = 'c6in.8xlarge'
    C6IN_12XLARGE = 'c6in.12xlarge'
    C6IN_16XLARGE = 'c6in.16xlarge'
    C6IN_24XLARGE = 'c6in.24xlarge'
    C6IN_32XLARGE = 'c6in.32xlarge'
    M6IN_LARGE = 'm6in.large'
    M6IN_XLARGE = 'm6in.xlarge'
    M6IN_2XLARGE = 'm6in.2xlarge'
    M6IN_4XLARGE = 'm6in.4xlarge'
    M6IN_8XLARGE = 'm6in.8xlarge'
    M6IN_12XLARGE = 'm6in.12xlarge'
    M6IN_16XLARGE = 'm6in.16xlarge'
    M6IN_24XLARGE = 'm6in.24xlarge'
    M6IN_32XLARGE = 'm6in.32xlarge'
    M6IDN_LARGE = 'm6idn.large'
    M6IDN_XLARGE = 'm6idn.xlarge'
    M6IDN_2XLARGE = 'm6idn.2xlarge'
    M6IDN_4XLARGE = 'm6idn.4xlarge'
    M6IDN_8XLARGE = 'm6idn.8xlarge'
    M6IDN_12XLARGE = 'm6idn.12xlarge'
    M6IDN_16XLARGE = 'm6idn.16xlarge'
    M6IDN_24XLARGE = 'm6idn.24xlarge'
    M6IDN_32XLARGE = 'm6idn.32xlarge'
    R6IN_LARGE = 'r6in.large'
    R6IN_XLARGE = 'r6in.xlarge'
    R6IN_2XLARGE = 'r6in.2xlarge'
    R6IN_4XLARGE = 'r6in.4xlarge'
    R6IN_8XLARGE = 'r6in.8xlarge'
    R6IN_12XLARGE = 'r6in.12xlarge'
    R6IN_16XLARGE = 'r6in.16xlarge'
    R6IN_24XLARGE = 'r6in.24xlarge'
    R6IN_32XLARGE = 'r6in.32xlarge'
    R6IDN_LARGE = 'r6idn.large'
    R6IDN_XLARGE = 'r6idn.xlarge'
    R6IDN_2XLARGE = 'r6idn.2xlarge'
    R6IDN_4XLARGE = 'r6idn.4xlarge'
    R6IDN_8XLARGE = 'r6idn.8xlarge'
    R6IDN_12XLARGE = 'r6idn.12xlarge'
    R6IDN_16XLARGE = 'r6idn.16xlarge'
    R6IDN_24XLARGE = 'r6idn.24xlarge'
    R6IDN_32XLARGE = 'r6idn.32xlarge'
    C7G_METAL = 'c7g.metal'
    M7G_MEDIUM = 'm7g.medium'
    M7G_LARGE = 'm7g.large'
    M7G_XLARGE = 'm7g.xlarge'
    M7G_2XLARGE = 'm7g.2xlarge'
    M7G_4XLARGE = 'm7g.4xlarge'
    M7G_8XLARGE = 'm7g.8xlarge'
    M7G_12XLARGE = 'm7g.12xlarge'
    M7G_16XLARGE = 'm7g.16xlarge'
    M7G_METAL = 'm7g.metal'
    R7G_MEDIUM = 'r7g.medium'
    R7G_LARGE = 'r7g.large'
    R7G_XLARGE = 'r7g.xlarge'
    R7G_2XLARGE = 'r7g.2xlarge'
    R7G_4XLARGE = 'r7g.4xlarge'
    R7G_8XLARGE = 'r7g.8xlarge'
    R7G_12XLARGE = 'r7g.12xlarge'
    R7G_16XLARGE = 'r7g.16xlarge'
    R7G_METAL = 'r7g.metal'
    C6IN_METAL = 'c6in.metal'
    M6IN_METAL = 'm6in.metal'
    M6IDN_METAL = 'm6idn.metal'
    R6IN_METAL = 'r6in.metal'
    R6IDN_METAL = 'r6idn.metal'
    INF2_XLARGE = 'inf2.xlarge'
    INF2_8XLARGE = 'inf2.8xlarge'
    INF2_24XLARGE = 'inf2.24xlarge'
    INF2_48XLARGE = 'inf2.48xlarge'
    TRN1N_32XLARGE = 'trn1n.32xlarge'
    I4G_LARGE = 'i4g.large'
    I4G_XLARGE = 'i4g.xlarge'
    I4G_2XLARGE = 'i4g.2xlarge'
    I4G_4XLARGE = 'i4g.4xlarge'
    I4G_8XLARGE = 'i4g.8xlarge'
    I4G_16XLARGE = 'i4g.16xlarge'
    HPC7G_4XLARGE = 'hpc7g.4xlarge'
    HPC7G_8XLARGE = 'hpc7g.8xlarge'
    HPC7G_16XLARGE = 'hpc7g.16xlarge'
    C7GN_MEDIUM = 'c7gn.medium'
    C7GN_LARGE = 'c7gn.large'
    C7GN_XLARGE = 'c7gn.xlarge'
    C7GN_2XLARGE = 'c7gn.2xlarge'
    C7GN_4XLARGE = 'c7gn.4xlarge'
    C7GN_8XLARGE = 'c7gn.8xlarge'
    C7GN_12XLARGE = 'c7gn.12xlarge'
    C7GN_16XLARGE = 'c7gn.16xlarge'
    P5_48XLARGE = 'p5.48xlarge'
    M7I_LARGE = 'm7i.large'
    M7I_XLARGE = 'm7i.xlarge'
    M7I_2XLARGE = 'm7i.2xlarge'
    M7I_4XLARGE = 'm7i.4xlarge'
    M7I_8XLARGE = 'm7i.8xlarge'
    M7I_12XLARGE = 'm7i.12xlarge'
    M7I_16XLARGE = 'm7i.16xlarge'
    M7I_24XLARGE = 'm7i.24xlarge'
    M7I_48XLARGE = 'm7i.48xlarge'
    M7I_FLEX_LARGE = 'm7i-flex.large'
    M7I_FLEX_XLARGE = 'm7i-flex.xlarge'
    M7I_FLEX_2XLARGE = 'm7i-flex.2xlarge'
    M7I_FLEX_4XLARGE = 'm7i-flex.4xlarge'
    M7I_FLEX_8XLARGE = 'm7i-flex.8xlarge'
    M7A_MEDIUM = 'm7a.medium'
    M7A_LARGE = 'm7a.large'
    M7A_XLARGE = 'm7a.xlarge'
    M7A_2XLARGE = 'm7a.2xlarge'
    M7A_4XLARGE = 'm7a.4xlarge'
    M7A_8XLARGE = 'm7a.8xlarge'
    M7A_12XLARGE = 'm7a.12xlarge'
    M7A_16XLARGE = 'm7a.16xlarge'
    M7A_24XLARGE = 'm7a.24xlarge'
    M7A_32XLARGE = 'm7a.32xlarge'
    M7A_48XLARGE = 'm7a.48xlarge'
    M7A_METAL_48XL = 'm7a.metal-48xl'
    HPC7A_12XLARGE = 'hpc7a.12xlarge'
    HPC7A_24XLARGE = 'hpc7a.24xlarge'
    HPC7A_48XLARGE = 'hpc7a.48xlarge'
    HPC7A_96XLARGE = 'hpc7a.96xlarge'
    C7GD_MEDIUM = 'c7gd.medium'
    C7GD_LARGE = 'c7gd.large'
    C7GD_XLARGE = 'c7gd.xlarge'
    C7GD_2XLARGE = 'c7gd.2xlarge'
    C7GD_4XLARGE = 'c7gd.4xlarge'
    C7GD_8XLARGE = 'c7gd.8xlarge'
    C7GD_12XLARGE = 'c7gd.12xlarge'
    C7GD_16XLARGE = 'c7gd.16xlarge'
    M7GD_MEDIUM = 'm7gd.medium'
    M7GD_LARGE = 'm7gd.large'
    M7GD_XLARGE = 'm7gd.xlarge'
    M7GD_2XLARGE = 'm7gd.2xlarge'
    M7GD_4XLARGE = 'm7gd.4xlarge'
    M7GD_8XLARGE = 'm7gd.8xlarge'
    M7GD_12XLARGE = 'm7gd.12xlarge'
    M7GD_16XLARGE = 'm7gd.16xlarge'
    R7GD_MEDIUM = 'r7gd.medium'
    R7GD_LARGE = 'r7gd.large'
    R7GD_XLARGE = 'r7gd.xlarge'
    R7GD_2XLARGE = 'r7gd.2xlarge'
    R7GD_4XLARGE = 'r7gd.4xlarge'
    R7GD_8XLARGE = 'r7gd.8xlarge'
    R7GD_12XLARGE = 'r7gd.12xlarge'
    R7GD_16XLARGE = 'r7gd.16xlarge'
    R7A_MEDIUM = 'r7a.medium'
    R7A_LARGE = 'r7a.large'
    R7A_XLARGE = 'r7a.xlarge'
    R7A_2XLARGE = 'r7a.2xlarge'
    R7A_4XLARGE = 'r7a.4xlarge'
    R7A_8XLARGE = 'r7a.8xlarge'
    R7A_12XLARGE = 'r7a.12xlarge'
    R7A_16XLARGE = 'r7a.16xlarge'
    R7A_24XLARGE = 'r7a.24xlarge'
    R7A_32XLARGE = 'r7a.32xlarge'
    R7A_48XLARGE = 'r7a.48xlarge'
    C7I_LARGE = 'c7i.large'
    C7I_XLARGE = 'c7i.xlarge'
    C7I_2XLARGE = 'c7i.2xlarge'
    C7I_4XLARGE = 'c7i.4xlarge'
    C7I_8XLARGE = 'c7i.8xlarge'
    C7I_12XLARGE = 'c7i.12xlarge'
    C7I_16XLARGE = 'c7i.16xlarge'
    C7I_24XLARGE = 'c7i.24xlarge'
    C7I_48XLARGE = 'c7i.48xlarge'
    MAC2_M2PRO_METAL = 'mac2-m2pro.metal'
    R7IZ_LARGE = 'r7iz.large'
    R7IZ_XLARGE = 'r7iz.xlarge'
    R7IZ_2XLARGE = 'r7iz.2xlarge'
    R7IZ_4XLARGE = 'r7iz.4xlarge'
    R7IZ_8XLARGE = 'r7iz.8xlarge'
    R7IZ_12XLARGE = 'r7iz.12xlarge'
    R7IZ_16XLARGE = 'r7iz.16xlarge'
    R7IZ_32XLARGE = 'r7iz.32xlarge'
    C7A_MEDIUM = 'c7a.medium'
    C7A_LARGE = 'c7a.large'
    C7A_XLARGE = 'c7a.xlarge'
    C7A_2XLARGE = 'c7a.2xlarge'
    C7A_4XLARGE = 'c7a.4xlarge'
    C7A_8XLARGE = 'c7a.8xlarge'
    C7A_12XLARGE = 'c7a.12xlarge'
    C7A_16XLARGE = 'c7a.16xlarge'
    C7A_24XLARGE = 'c7a.24xlarge'
    C7A_32XLARGE = 'c7a.32xlarge'
    C7A_48XLARGE = 'c7a.48xlarge'
    C7A_METAL_48XL = 'c7a.metal-48xl'
    R7A_METAL_48XL = 'r7a.metal-48xl'
    R7I_LARGE = 'r7i.large'
    R7I_XLARGE = 'r7i.xlarge'
    R7I_2XLARGE = 'r7i.2xlarge'
    R7I_4XLARGE = 'r7i.4xlarge'
    R7I_8XLARGE = 'r7i.8xlarge'
    R7I_12XLARGE = 'r7i.12xlarge'
    R7I_16XLARGE = 'r7i.16xlarge'
    R7I_24XLARGE = 'r7i.24xlarge'
    R7I_48XLARGE = 'r7i.48xlarge'
    DL2Q_24XLARGE = 'dl2q.24xlarge'
    MAC2_M2_METAL = 'mac2-m2.metal'
    I4I_12XLARGE = 'i4i.12xlarge'
    I4I_24XLARGE = 'i4i.24xlarge'
    C7I_METAL_24XL = 'c7i.metal-24xl'
    C7I_METAL_48XL = 'c7i.metal-48xl'
    M7I_METAL_24XL = 'm7i.metal-24xl'
    M7I_METAL_48XL = 'm7i.metal-48xl'
    R7I_METAL_24XL = 'r7i.metal-24xl'
    R7I_METAL_48XL = 'r7i.metal-48xl'
    R7IZ_METAL_16XL = 'r7iz.metal-16xl'
    R7IZ_METAL_32XL = 'r7iz.metal-32xl'
    C7GD_METAL = 'c7gd.metal'
    M7GD_METAL = 'm7gd.metal'
    R7GD_METAL = 'r7gd.metal'
    G6_XLARGE = 'g6.xlarge'
    G6_2XLARGE = 'g6.2xlarge'
    G6_4XLARGE = 'g6.4xlarge'
    G6_8XLARGE = 'g6.8xlarge'
    G6_12XLARGE = 'g6.12xlarge'
    G6_16XLARGE = 'g6.16xlarge'
    G6_24XLARGE = 'g6.24xlarge'
    G6_48XLARGE = 'g6.48xlarge'
    GR6_4XLARGE = 'gr6.4xlarge'
    GR6_8XLARGE = 'gr6.8xlarge'
    C7I_FLEX_LARGE = 'c7i-flex.large'
    C7I_FLEX_XLARGE = 'c7i-flex.xlarge'
    C7I_FLEX_2XLARGE = 'c7i-flex.2xlarge'
    C7I_FLEX_4XLARGE = 'c7i-flex.4xlarge'
    C7I_FLEX_8XLARGE = 'c7i-flex.8xlarge'
    U7I_12TB_224XLARGE = 'u7i-12tb.224xlarge'
    U7IN_16TB_224XLARGE = 'u7in-16tb.224xlarge'
    U7IN_24TB_224XLARGE = 'u7in-24tb.224xlarge'
    U7IN_32TB_224XLARGE = 'u7in-32tb.224xlarge'
    U7IB_12TB_224XLARGE = 'u7ib-12tb.224xlarge'
    C7GN_METAL = 'c7gn.metal'
    R8G_MEDIUM = 'r8g.medium'
    R8G_LARGE = 'r8g.large'
    R8G_XLARGE = 'r8g.xlarge'
    R8G_2XLARGE = 'r8g.2xlarge'
    R8G_4XLARGE = 'r8g.4xlarge'
    R8G_8XLARGE = 'r8g.8xlarge'
    R8G_12XLARGE = 'r8g.12xlarge'
    R8G_16XLARGE = 'r8g.16xlarge'
    R8G_24XLARGE = 'r8g.24xlarge'
    R8G_48XLARGE = 'r8g.48xlarge'
    R8G_METAL_24XL = 'r8g.metal-24xl'
    R8G_METAL_48XL = 'r8g.metal-48xl'
    MAC2_M1ULTRA_METAL = 'mac2-m1ultra.metal'
    G6E_XLARGE = 'g6e.xlarge'
    G6E_2XLARGE = 'g6e.2xlarge'
    G6E_4XLARGE = 'g6e.4xlarge'
    G6E_8XLARGE = 'g6e.8xlarge'
    G6E_12XLARGE = 'g6e.12xlarge'
    G6E_16XLARGE = 'g6e.16xlarge'
    G6E_24XLARGE = 'g6e.24xlarge'
    G6E_48XLARGE = 'g6e.48xlarge'
    C8G_MEDIUM = 'c8g.medium'
    C8G_LARGE = 'c8g.large'
    C8G_XLARGE = 'c8g.xlarge'
    C8G_2XLARGE = 'c8g.2xlarge'
    C8G_4XLARGE = 'c8g.4xlarge'
    C8G_8XLARGE = 'c8g.8xlarge'
    C8G_12XLARGE = 'c8g.12xlarge'
    C8G_16XLARGE = 'c8g.16xlarge'
    C8G_24XLARGE = 'c8g.24xlarge'
    C8G_48XLARGE = 'c8g.48xlarge'
    C8G_METAL_24XL = 'c8g.metal-24xl'
    C8G_METAL_48XL = 'c8g.metal-48xl'
    M8G_MEDIUM = 'm8g.medium'
    M8G_LARGE = 'm8g.large'
    M8G_XLARGE = 'm8g.xlarge'
    M8G_2XLARGE = 'm8g.2xlarge'
    M8G_4XLARGE = 'm8g.4xlarge'
    M8G_8XLARGE = 'm8g.8xlarge'
    M8G_12XLARGE = 'm8g.12xlarge'
    M8G_16XLARGE = 'm8g.16xlarge'
    M8G_24XLARGE = 'm8g.24xlarge'
    M8G_48XLARGE = 'm8g.48xlarge'
    M8G_METAL_24XL = 'm8g.metal-24xl'
    M8G_METAL_48XL = 'm8g.metal-48xl'
    X8G_MEDIUM = 'x8g.medium'
    X8G_LARGE = 'x8g.large'
    X8G_XLARGE = 'x8g.xlarge'
    X8G_2XLARGE = 'x8g.2xlarge'
    X8G_4XLARGE = 'x8g.4xlarge'
    X8G_8XLARGE = 'x8g.8xlarge'
    X8G_12XLARGE = 'x8g.12xlarge'
    X8G_16XLARGE = 'x8g.16xlarge'
    X8G_24XLARGE = 'x8g.24xlarge'
    X8G_48XLARGE = 'x8g.48xlarge'
    X8G_METAL_24XL = 'x8g.metal-24xl'
    X8G_METAL_48XL = 'x8g.metal-48xl'
    I7IE_LARGE = 'i7ie.large'
    I7IE_XLARGE = 'i7ie.xlarge'
    I7IE_2XLARGE = 'i7ie.2xlarge'
    I7IE_3XLARGE = 'i7ie.3xlarge'
    I7IE_6XLARGE = 'i7ie.6xlarge'
    I7IE_12XLARGE = 'i7ie.12xlarge'
    I7IE_18XLARGE = 'i7ie.18xlarge'
    I7IE_24XLARGE = 'i7ie.24xlarge'
    I7IE_48XLARGE = 'i7ie.48xlarge'
    I8G_LARGE = 'i8g.large'
    I8G_XLARGE = 'i8g.xlarge'
    I8G_2XLARGE = 'i8g.2xlarge'
    I8G_4XLARGE = 'i8g.4xlarge'
    I8G_8XLARGE = 'i8g.8xlarge'
    I8G_12XLARGE = 'i8g.12xlarge'
    I8G_16XLARGE = 'i8g.16xlarge'
    I8G_24XLARGE = 'i8g.24xlarge'
    I8G_METAL_24XL = 'i8g.metal-24xl'
    U7I_6TB_112XLARGE = 'u7i-6tb.112xlarge'
    U7I_8TB_112XLARGE = 'u7i-8tb.112xlarge'
    U7INH_32TB_480XLARGE = 'u7inh-32tb.480xlarge'
    P5E_48XLARGE = 'p5e.48xlarge'
    P5EN_48XLARGE = 'p5en.48xlarge'
    F2_12XLARGE = 'f2.12xlarge'
    F2_48XLARGE = 'f2.48xlarge'
    TRN2_48XLARGE = 'trn2.48xlarge'


class InstanceTypeHypervisor(_enum.Enum):
    NITRO = 'nitro'
    XEN = 'xen'


InternetGatewayId = _ta.NewType('InternetGatewayId', str)


class IpSource(_enum.Enum):
    AMAZON = 'amazon'
    BYOIP = 'byoip'
    NONE = 'none'


class Ipv6AddressAttribute(_enum.Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'


Ipv6Flag = _ta.NewType('Ipv6Flag', bool)

KernelId = _ta.NewType('KernelId', str)

KeyPairId = _ta.NewType('KeyPairId', str)

KeyPairName = _ta.NewType('KeyPairName', str)


class KeyType(_enum.Enum):
    RSA = 'rsa'
    ED25519 = 'ed25519'


LaunchTemplateId = _ta.NewType('LaunchTemplateId', str)

LocalGatewayId = _ta.NewType('LocalGatewayId', str)


class MarketType(_enum.Enum):
    SPOT = 'spot'
    CAPACITY_BLOCK = 'capacity-block'


MaxIpv4AddrPerInterface = _ta.NewType('MaxIpv4AddrPerInterface', int)

MaxIpv6AddrPerInterface = _ta.NewType('MaxIpv6AddrPerInterface', int)

MaxNetworkInterfaces = _ta.NewType('MaxNetworkInterfaces', int)

MaximumBandwidthInMbps = _ta.NewType('MaximumBandwidthInMbps', int)

MaximumEfaInterfaces = _ta.NewType('MaximumEfaInterfaces', int)

MaximumIops = _ta.NewType('MaximumIops', int)

MaximumNetworkCards = _ta.NewType('MaximumNetworkCards', int)

MaximumThroughputInMBps = _ta.NewType('MaximumThroughputInMBps', float)

MediaDeviceCount = _ta.NewType('MediaDeviceCount', int)

MediaDeviceManufacturerName = _ta.NewType('MediaDeviceManufacturerName', str)

MediaDeviceMemorySize = _ta.NewType('MediaDeviceMemorySize', int)

MediaDeviceName = _ta.NewType('MediaDeviceName', str)

MemorySize = _ta.NewType('MemorySize', int)


class MonitoringState(_enum.Enum):
    DISABLED = 'disabled'
    DISABLING = 'disabling'
    ENABLED = 'enabled'
    PENDING = 'pending'


NatGatewayId = _ta.NewType('NatGatewayId', str)

NetworkCardIndex = _ta.NewType('NetworkCardIndex', int)

NetworkInterfaceId = _ta.NewType('NetworkInterfaceId', str)


class NetworkInterfaceStatus(_enum.Enum):
    AVAILABLE = 'available'
    ASSOCIATED = 'associated'
    ATTACHING = 'attaching'
    IN_USE = 'in-use'
    DETACHING = 'detaching'


class NetworkInterfaceType(_enum.Enum):
    INTERFACE = 'interface'
    NAT_GATEWAY = 'natGateway'
    EFA = 'efa'
    EFA_ONLY = 'efa-only'
    TRUNK = 'trunk'
    LOAD_BALANCER = 'load_balancer'
    NETWORK_LOAD_BALANCER = 'network_load_balancer'
    VPC_ENDPOINT = 'vpc_endpoint'
    BRANCH = 'branch'
    TRANSIT_GATEWAY = 'transit_gateway'
    LAMBDA = 'lambda'
    QUICKSIGHT = 'quicksight'
    GLOBAL_ACCELERATOR_MANAGED = 'global_accelerator_managed'
    API_GATEWAY_MANAGED = 'api_gateway_managed'
    GATEWAY_LOAD_BALANCER = 'gateway_load_balancer'
    GATEWAY_LOAD_BALANCER_ENDPOINT = 'gateway_load_balancer_endpoint'
    IOT_RULES_MANAGED = 'iot_rules_managed'
    AWS_CODESTAR_CONNECTIONS_MANAGED = 'aws_codestar_connections_managed'


NetworkPerformance = _ta.NewType('NetworkPerformance', str)

NeuronDeviceCoreCount = _ta.NewType('NeuronDeviceCoreCount', int)

NeuronDeviceCoreVersion = _ta.NewType('NeuronDeviceCoreVersion', int)

NeuronDeviceCount = _ta.NewType('NeuronDeviceCount', int)

NeuronDeviceMemorySize = _ta.NewType('NeuronDeviceMemorySize', int)

NeuronDeviceName = _ta.NewType('NeuronDeviceName', str)

NextToken = _ta.NewType('NextToken', str)


class NitroEnclavesSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    SUPPORTED = 'supported'


class NitroTpmSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    SUPPORTED = 'supported'


NitroTpmSupportedVersionType = _ta.NewType('NitroTpmSupportedVersionType', str)

PeakBandwidthInGbps = _ta.NewType('PeakBandwidthInGbps', float)


class PhcSupport(_enum.Enum):
    UNSUPPORTED = 'unsupported'
    SUPPORTED = 'supported'


PlacementGroupId = _ta.NewType('PlacementGroupId', str)

PlacementGroupName = _ta.NewType('PlacementGroupName', str)


class PlacementGroupStrategy(_enum.Enum):
    CLUSTER = 'cluster'
    PARTITION = 'partition'
    SPREAD = 'spread'


class PlatformValues(_enum.Enum):
    WINDOWS = 'Windows'


PrefixListResourceId = _ta.NewType('PrefixListResourceId', str)

ProcessorSustainedClockSpeed = _ta.NewType('ProcessorSustainedClockSpeed', float)


class ProductCodeValues(_enum.Enum):
    DEVPAY = 'devpay'
    MARKETPLACE = 'marketplace'


RamdiskId = _ta.NewType('RamdiskId', str)


class ResourceType(_enum.Enum):
    CAPACITY_RESERVATION = 'capacity-reservation'
    CLIENT_VPN_ENDPOINT = 'client-vpn-endpoint'
    CUSTOMER_GATEWAY = 'customer-gateway'
    CARRIER_GATEWAY = 'carrier-gateway'
    COIP_POOL = 'coip-pool'
    DECLARATIVE_POLICIES_REPORT = 'declarative-policies-report'
    DEDICATED_HOST = 'dedicated-host'
    DHCP_OPTIONS = 'dhcp-options'
    EGRESS_ONLY_INTERNET_GATEWAY = 'egress-only-internet-gateway'
    ELASTIC_IP = 'elastic-ip'
    ELASTIC_GPU = 'elastic-gpu'
    EXPORT_IMAGE_TASK = 'export-image-task'
    EXPORT_INSTANCE_TASK = 'export-instance-task'
    FLEET = 'fleet'
    FPGA_IMAGE = 'fpga-image'
    HOST_RESERVATION = 'host-reservation'
    IMAGE = 'image'
    IMPORT_IMAGE_TASK = 'import-image-task'
    IMPORT_SNAPSHOT_TASK = 'import-snapshot-task'
    INSTANCE = 'instance'
    INSTANCE_EVENT_WINDOW = 'instance-event-window'
    INTERNET_GATEWAY = 'internet-gateway'
    IPAM = 'ipam'
    IPAM_POOL = 'ipam-pool'
    IPAM_SCOPE = 'ipam-scope'
    IPV4POOL_EC2 = 'ipv4pool-ec2'
    IPV6POOL_EC2 = 'ipv6pool-ec2'
    KEY_PAIR = 'key-pair'
    LAUNCH_TEMPLATE = 'launch-template'
    LOCAL_GATEWAY = 'local-gateway'
    LOCAL_GATEWAY_ROUTE_TABLE = 'local-gateway-route-table'
    LOCAL_GATEWAY_VIRTUAL_INTERFACE = 'local-gateway-virtual-interface'
    LOCAL_GATEWAY_VIRTUAL_INTERFACE_GROUP = 'local-gateway-virtual-interface-group'
    LOCAL_GATEWAY_ROUTE_TABLE_VPC_ASSOCIATION = 'local-gateway-route-table-vpc-association'
    LOCAL_GATEWAY_ROUTE_TABLE_VIRTUAL_INTERFACE_GROUP_ASSOCIATION = 'local-gateway-route-table-virtual-interface-group-association'
    NATGATEWAY = 'natgateway'
    NETWORK_ACL = 'network-acl'
    NETWORK_INTERFACE = 'network-interface'
    NETWORK_INSIGHTS_ANALYSIS = 'network-insights-analysis'
    NETWORK_INSIGHTS_PATH = 'network-insights-path'
    NETWORK_INSIGHTS_ACCESS_SCOPE = 'network-insights-access-scope'
    NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSIS = 'network-insights-access-scope-analysis'
    PLACEMENT_GROUP = 'placement-group'
    PREFIX_LIST = 'prefix-list'
    REPLACE_ROOT_VOLUME_TASK = 'replace-root-volume-task'
    RESERVED_INSTANCES = 'reserved-instances'
    ROUTE_TABLE = 'route-table'
    SECURITY_GROUP = 'security-group'
    SECURITY_GROUP_RULE = 'security-group-rule'
    SNAPSHOT = 'snapshot'
    SPOT_FLEET_REQUEST = 'spot-fleet-request'
    SPOT_INSTANCES_REQUEST = 'spot-instances-request'
    SUBNET = 'subnet'
    SUBNET_CIDR_RESERVATION = 'subnet-cidr-reservation'
    TRAFFIC_MIRROR_FILTER = 'traffic-mirror-filter'
    TRAFFIC_MIRROR_SESSION = 'traffic-mirror-session'
    TRAFFIC_MIRROR_TARGET = 'traffic-mirror-target'
    TRANSIT_GATEWAY = 'transit-gateway'
    TRANSIT_GATEWAY_ATTACHMENT = 'transit-gateway-attachment'
    TRANSIT_GATEWAY_CONNECT_PEER = 'transit-gateway-connect-peer'
    TRANSIT_GATEWAY_MULTICAST_DOMAIN = 'transit-gateway-multicast-domain'
    TRANSIT_GATEWAY_POLICY_TABLE = 'transit-gateway-policy-table'
    TRANSIT_GATEWAY_ROUTE_TABLE = 'transit-gateway-route-table'
    TRANSIT_GATEWAY_ROUTE_TABLE_ANNOUNCEMENT = 'transit-gateway-route-table-announcement'
    VOLUME = 'volume'
    VPC = 'vpc'
    VPC_ENDPOINT = 'vpc-endpoint'
    VPC_ENDPOINT_CONNECTION = 'vpc-endpoint-connection'
    VPC_ENDPOINT_SERVICE = 'vpc-endpoint-service'
    VPC_ENDPOINT_SERVICE_PERMISSION = 'vpc-endpoint-service-permission'
    VPC_PEERING_CONNECTION = 'vpc-peering-connection'
    VPN_CONNECTION = 'vpn-connection'
    VPN_GATEWAY = 'vpn-gateway'
    VPC_FLOW_LOG = 'vpc-flow-log'
    CAPACITY_RESERVATION_FLEET = 'capacity-reservation-fleet'
    TRAFFIC_MIRROR_FILTER_RULE = 'traffic-mirror-filter-rule'
    VPC_ENDPOINT_CONNECTION_DEVICE_TYPE = 'vpc-endpoint-connection-device-type'
    VERIFIED_ACCESS_INSTANCE = 'verified-access-instance'
    VERIFIED_ACCESS_GROUP = 'verified-access-group'
    VERIFIED_ACCESS_ENDPOINT = 'verified-access-endpoint'
    VERIFIED_ACCESS_POLICY = 'verified-access-policy'
    VERIFIED_ACCESS_TRUST_PROVIDER = 'verified-access-trust-provider'
    VPN_CONNECTION_DEVICE_TYPE = 'vpn-connection-device-type'
    VPC_BLOCK_PUBLIC_ACCESS_EXCLUSION = 'vpc-block-public-access-exclusion'
    ROUTE_SERVER = 'route-server'
    ROUTE_SERVER_ENDPOINT = 'route-server-endpoint'
    ROUTE_SERVER_PEER = 'route-server-peer'
    IPAM_RESOURCE_DISCOVERY = 'ipam-resource-discovery'
    IPAM_RESOURCE_DISCOVERY_ASSOCIATION = 'ipam-resource-discovery-association'
    INSTANCE_CONNECT_ENDPOINT = 'instance-connect-endpoint'
    VERIFIED_ACCESS_ENDPOINT_TARGET = 'verified-access-endpoint-target'
    IPAM_EXTERNAL_RESOURCE_VERIFICATION_TOKEN = 'ipam-external-resource-verification-token'


class RootDeviceType(_enum.Enum):
    EBS = 'ebs'
    INSTANCE_STORE = 'instance-store'


RouteGatewayId = _ta.NewType('RouteGatewayId', str)


class RouteOrigin(_enum.Enum):
    CREATE_ROUTE_TABLE = 'CreateRouteTable'
    CREATE_ROUTE = 'CreateRoute'
    ENABLE_VGW_ROUTE_PROPAGATION = 'EnableVgwRoutePropagation'


class RouteState(_enum.Enum):
    ACTIVE = 'active'
    BLACKHOLE = 'blackhole'


class RouteTableAssociationStateCode(_enum.Enum):
    ASSOCIATING = 'associating'
    ASSOCIATED = 'associated'
    DISASSOCIATING = 'disassociating'
    DISASSOCIATED = 'disassociated'
    FAILED = 'failed'


RouteTableId = _ta.NewType('RouteTableId', str)

RunInstancesUserData = _ta.NewType('RunInstancesUserData', str)

SecurityGroupId = _ta.NewType('SecurityGroupId', str)

SecurityGroupName = _ta.NewType('SecurityGroupName', str)


class ServiceManaged(_enum.Enum):
    ALB = 'alb'
    NLB = 'nlb'


class ShutdownBehavior(_enum.Enum):
    STOP = 'stop'
    TERMINATE = 'terminate'


SnapshotId = _ta.NewType('SnapshotId', str)


class SpotInstanceType(_enum.Enum):
    ONE_TIME = 'one-time'
    PERSISTENT = 'persistent'


SubnetCidrAssociationId = _ta.NewType('SubnetCidrAssociationId', str)


class SubnetCidrBlockStateCode(_enum.Enum):
    ASSOCIATING = 'associating'
    ASSOCIATED = 'associated'
    DISASSOCIATING = 'disassociating'
    DISASSOCIATED = 'disassociated'
    FAILING = 'failing'
    FAILED = 'failed'


SubnetId = _ta.NewType('SubnetId', str)


class SubnetState(_enum.Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'


class SupportedAdditionalProcessorFeature(_enum.Enum):
    AMD_SEV_SNP = 'amd-sev-snp'


class Tenancy(_enum.Enum):
    DEFAULT = 'default'
    DEDICATED = 'dedicated'
    HOST = 'host'


ThreadsPerCore = _ta.NewType('ThreadsPerCore', int)

TotalMediaMemory = _ta.NewType('TotalMediaMemory', int)

TotalNeuronMemory = _ta.NewType('TotalNeuronMemory', int)


class TpmSupportValues(_enum.Enum):
    V2_0 = 'v2.0'


TransitGatewayId = _ta.NewType('TransitGatewayId', str)


class UsageClassType(_enum.Enum):
    SPOT = 'spot'
    ON_DEMAND = 'on-demand'
    CAPACITY_BLOCK = 'capacity-block'


VCpuCount = _ta.NewType('VCpuCount', int)


class VirtualizationType(_enum.Enum):
    HVM = 'hvm'
    PARAVIRTUAL = 'paravirtual'


class VolumeType(_enum.Enum):
    STANDARD = 'standard'
    IO1 = 'io1'
    IO2 = 'io2'
    GP2 = 'gp2'
    SC1 = 'sc1'
    ST1 = 'st1'
    GP3 = 'gp3'


class VpcCidrBlockStateCode(_enum.Enum):
    ASSOCIATING = 'associating'
    ASSOCIATED = 'associated'
    DISASSOCIATING = 'disassociating'
    DISASSOCIATED = 'disassociated'
    FAILING = 'failing'
    FAILED = 'failed'


class VpcEncryptionControlExclusionState(_enum.Enum):
    ENABLING = 'enabling'
    ENABLED = 'enabled'
    DISABLING = 'disabling'
    DISABLED = 'disabled'


VpcEncryptionControlId = _ta.NewType('VpcEncryptionControlId', str)


class VpcEncryptionControlMode(_enum.Enum):
    MONITOR = 'monitor'
    ENFORCE = 'enforce'


class VpcEncryptionControlState(_enum.Enum):
    ENFORCE_IN_PROGRESS = 'enforce-in-progress'
    MONITOR_IN_PROGRESS = 'monitor-in-progress'
    ENFORCE_FAILED = 'enforce-failed'
    MONITOR_FAILED = 'monitor-failed'
    DELETING = 'deleting'
    DELETED = 'deleted'
    AVAILABLE = 'available'
    CREATING = 'creating'
    DELETE_FAILED = 'delete-failed'


VpcEndpointId = _ta.NewType('VpcEndpointId', str)

VpcId = _ta.NewType('VpcId', str)

VpcPeeringConnectionId = _ta.NewType('VpcPeeringConnectionId', str)


class VpcState(_enum.Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'


TotalFpgaMemory = _ta.NewType('TotalFpgaMemory', int)

TotalGpuMemory = _ta.NewType('TotalGpuMemory', int)

TotalInferenceMemory = _ta.NewType('TotalInferenceMemory', int)


@_dc.dataclass(frozen=True, kw_only=True)
class Address(
    _base.Shape,
    shape_name='Address',
):
    allocation_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AllocationId',
        serialization_name='allocationId',
        shape_name='String',
    ))

    association_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociationId',
        serialization_name='associationId',
        shape_name='String',
    ))

    domain: DomainType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Domain',
        serialization_name='domain',
        shape_name='DomainType',
    ))

    network_interface_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        serialization_name='networkInterfaceId',
        shape_name='String',
    ))

    network_interface_owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaceOwnerId',
        serialization_name='networkInterfaceOwnerId',
        shape_name='String',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    public_ipv4_pool: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicIpv4Pool',
        serialization_name='publicIpv4Pool',
        shape_name='String',
    ))

    network_border_group: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkBorderGroup',
        serialization_name='networkBorderGroup',
        shape_name='String',
    ))

    customer_owned_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CustomerOwnedIp',
        serialization_name='customerOwnedIp',
        shape_name='String',
    ))

    customer_owned_ipv4_pool: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CustomerOwnedIpv4Pool',
        serialization_name='customerOwnedIpv4Pool',
        shape_name='String',
    ))

    carrier_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CarrierIp',
        serialization_name='carrierIp',
        shape_name='String',
    ))

    service_managed: ServiceManaged | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ServiceManaged',
        serialization_name='serviceManaged',
        shape_name='ServiceManaged',
    ))

    instance_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceId',
        serialization_name='instanceId',
        shape_name='String',
    ))

    public_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicIp',
        serialization_name='publicIp',
        shape_name='String',
    ))


AllocationIdList: _ta.TypeAlias = _ta.Sequence[AllocationId]

ArchitectureTypeList: _ta.TypeAlias = _ta.Sequence[ArchitectureType]


@_dc.dataclass(frozen=True, kw_only=True)
class AttachmentEnaSrdUdpSpecification(
    _base.Shape,
    shape_name='AttachmentEnaSrdUdpSpecification',
):
    ena_srd_udp_enabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdUdpEnabled',
        serialization_name='enaSrdUdpEnabled',
        shape_name='Boolean',
    ))


BandwidthWeightingTypeList: _ta.TypeAlias = _ta.Sequence[BandwidthWeightingType]


@_dc.dataclass(frozen=True, kw_only=True)
class BlockPublicAccessStates(
    _base.Shape,
    shape_name='BlockPublicAccessStates',
):
    internet_gateway_block_mode: BlockPublicAccessMode | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InternetGatewayBlockMode',
        serialization_name='internetGatewayBlockMode',
        shape_name='BlockPublicAccessMode',
    ))


BootModeTypeList: _ta.TypeAlias = _ta.Sequence[BootModeType]


@_dc.dataclass(frozen=True, kw_only=True)
class CapacityReservationTarget(
    _base.Shape,
    shape_name='CapacityReservationTarget',
):
    capacity_reservation_id: CapacityReservationId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationId',
        shape_name='CapacityReservationId',
    ))

    capacity_reservation_resource_group_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationResourceGroupArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CapacityReservationTargetResponse(
    _base.Shape,
    shape_name='CapacityReservationTargetResponse',
):
    capacity_reservation_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationId',
        serialization_name='capacityReservationId',
        shape_name='String',
    ))

    capacity_reservation_resource_group_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationResourceGroupArn',
        serialization_name='capacityReservationResourceGroupArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ConnectionTrackingConfiguration(
    _base.Shape,
    shape_name='ConnectionTrackingConfiguration',
):
    tcp_established_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TcpEstablishedTimeout',
        serialization_name='tcpEstablishedTimeout',
        shape_name='Integer',
    ))

    udp_stream_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UdpStreamTimeout',
        serialization_name='udpStreamTimeout',
        shape_name='Integer',
    ))

    udp_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UdpTimeout',
        serialization_name='udpTimeout',
        shape_name='Integer',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ConnectionTrackingSpecificationRequest(
    _base.Shape,
    shape_name='ConnectionTrackingSpecificationRequest',
):
    tcp_established_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TcpEstablishedTimeout',
        shape_name='Integer',
    ))

    udp_stream_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UdpStreamTimeout',
        shape_name='Integer',
    ))

    udp_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UdpTimeout',
        shape_name='Integer',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ConnectionTrackingSpecificationResponse(
    _base.Shape,
    shape_name='ConnectionTrackingSpecificationResponse',
):
    tcp_established_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TcpEstablishedTimeout',
        serialization_name='tcpEstablishedTimeout',
        shape_name='Integer',
    ))

    udp_stream_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UdpStreamTimeout',
        serialization_name='udpStreamTimeout',
        shape_name='Integer',
    ))

    udp_timeout: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UdpTimeout',
        serialization_name='udpTimeout',
        shape_name='Integer',
    ))


CoreCountList: _ta.TypeAlias = _ta.Sequence[CoreCount]


@_dc.dataclass(frozen=True, kw_only=True)
class CpuOptions(
    _base.Shape,
    shape_name='CpuOptions',
):
    core_count: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CoreCount',
        serialization_name='coreCount',
        shape_name='Integer',
    ))

    threads_per_core: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ThreadsPerCore',
        serialization_name='threadsPerCore',
        shape_name='Integer',
    ))

    amd_sev_snp: AmdSevSnpSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AmdSevSnp',
        serialization_name='amdSevSnp',
        shape_name='AmdSevSnpSpecification',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CpuOptionsRequest(
    _base.Shape,
    shape_name='CpuOptionsRequest',
):
    core_count: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CoreCount',
        shape_name='Integer',
    ))

    threads_per_core: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ThreadsPerCore',
        shape_name='Integer',
    ))

    amd_sev_snp: AmdSevSnpSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AmdSevSnp',
        shape_name='AmdSevSnpSpecification',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CreateRouteRequest(
    _base.Shape,
    shape_name='CreateRouteRequest',
):
    destination_prefix_list_id: PrefixListResourceId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationPrefixListId',
        shape_name='PrefixListResourceId',
    ))

    vpc_endpoint_id: VpcEndpointId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcEndpointId',
        shape_name='VpcEndpointId',
    ))

    transit_gateway_id: TransitGatewayId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TransitGatewayId',
        shape_name='TransitGatewayId',
    ))

    local_gateway_id: LocalGatewayId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LocalGatewayId',
        shape_name='LocalGatewayId',
    ))

    carrier_gateway_id: CarrierGatewayId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CarrierGatewayId',
        shape_name='CarrierGatewayId',
    ))

    core_network_arn: CoreNetworkArn | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CoreNetworkArn',
        shape_name='CoreNetworkArn',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    route_table_id: RouteTableId = _dc.field(metadata=_base.field_metadata(
        member_name='RouteTableId',
        serialization_name='routeTableId',
        shape_name='RouteTableId',
    ))

    destination_cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationCidrBlock',
        serialization_name='destinationCidrBlock',
        shape_name='String',
    ))

    gateway_id: RouteGatewayId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GatewayId',
        serialization_name='gatewayId',
        shape_name='RouteGatewayId',
    ))

    destination_ipv6_cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationIpv6CidrBlock',
        serialization_name='destinationIpv6CidrBlock',
        shape_name='String',
    ))

    egress_only_internet_gateway_id: EgressOnlyInternetGatewayId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EgressOnlyInternetGatewayId',
        serialization_name='egressOnlyInternetGatewayId',
        shape_name='EgressOnlyInternetGatewayId',
    ))

    instance_id: InstanceId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceId',
        serialization_name='instanceId',
        shape_name='InstanceId',
    ))

    network_interface_id: NetworkInterfaceId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        serialization_name='networkInterfaceId',
        shape_name='NetworkInterfaceId',
    ))

    vpc_peering_connection_id: VpcPeeringConnectionId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcPeeringConnectionId',
        serialization_name='vpcPeeringConnectionId',
        shape_name='VpcPeeringConnectionId',
    ))

    nat_gateway_id: NatGatewayId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NatGatewayId',
        serialization_name='natGatewayId',
        shape_name='NatGatewayId',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CreateRouteResult(
    _base.Shape,
    shape_name='CreateRouteResult',
):
    return_: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Return',
        serialization_name='return',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CreateSecurityGroupResult(
    _base.Shape,
    shape_name='CreateSecurityGroupResult',
):
    group_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupId',
        serialization_name='groupId',
        shape_name='String',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    security_group_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SecurityGroupArn',
        serialization_name='securityGroupArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CreditSpecificationRequest(
    _base.Shape,
    shape_name='CreditSpecificationRequest',
):
    cpu_credits: str = _dc.field(metadata=_base.field_metadata(
        member_name='CpuCredits',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DeleteRouteRequest(
    _base.Shape,
    shape_name='DeleteRouteRequest',
):
    destination_prefix_list_id: PrefixListResourceId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationPrefixListId',
        shape_name='PrefixListResourceId',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    route_table_id: RouteTableId = _dc.field(metadata=_base.field_metadata(
        member_name='RouteTableId',
        serialization_name='routeTableId',
        shape_name='RouteTableId',
    ))

    destination_cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationCidrBlock',
        serialization_name='destinationCidrBlock',
        shape_name='String',
    ))

    destination_ipv6_cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationIpv6CidrBlock',
        serialization_name='destinationIpv6CidrBlock',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DeleteRouteTableRequest(
    _base.Shape,
    shape_name='DeleteRouteTableRequest',
):
    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    route_table_id: RouteTableId = _dc.field(metadata=_base.field_metadata(
        member_name='RouteTableId',
        serialization_name='routeTableId',
        shape_name='RouteTableId',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DeleteSecurityGroupRequest(
    _base.Shape,
    shape_name='DeleteSecurityGroupRequest',
):
    group_id: SecurityGroupId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupId',
        shape_name='SecurityGroupId',
    ))

    group_name: SecurityGroupName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupName',
        shape_name='SecurityGroupName',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DeleteSecurityGroupResult(
    _base.Shape,
    shape_name='DeleteSecurityGroupResult',
):
    return_: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Return',
        serialization_name='return',
        shape_name='Boolean',
    ))

    group_id: SecurityGroupId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupId',
        serialization_name='groupId',
        shape_name='SecurityGroupId',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DiskInfo(
    _base.Shape,
    shape_name='DiskInfo',
):
    size_in_gb: DiskSize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SizeInGB',
        serialization_name='sizeInGB',
        shape_name='DiskSize',
    ))

    count: DiskCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Count',
        serialization_name='count',
        shape_name='DiskCount',
    ))

    type: DiskType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Type',
        serialization_name='type',
        shape_name='DiskType',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class EbsBlockDevice(
    _base.Shape,
    shape_name='EbsBlockDevice',
):
    delete_on_termination: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        serialization_name='deleteOnTermination',
        shape_name='Boolean',
    ))

    iops: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Iops',
        serialization_name='iops',
        shape_name='Integer',
    ))

    snapshot_id: SnapshotId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SnapshotId',
        serialization_name='snapshotId',
        shape_name='SnapshotId',
    ))

    volume_size: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VolumeSize',
        serialization_name='volumeSize',
        shape_name='Integer',
    ))

    volume_type: VolumeType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VolumeType',
        serialization_name='volumeType',
        shape_name='VolumeType',
    ))

    kms_key_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KmsKeyId',
        serialization_name='kmsKeyId',
        shape_name='String',
    ))

    throughput: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Throughput',
        serialization_name='throughput',
        shape_name='Integer',
    ))

    outpost_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OutpostArn',
        serialization_name='outpostArn',
        shape_name='String',
    ))

    encrypted: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Encrypted',
        serialization_name='encrypted',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class EbsOptimizedInfo(
    _base.Shape,
    shape_name='EbsOptimizedInfo',
):
    baseline_bandwidth_in_mbps: BaselineBandwidthInMbps | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BaselineBandwidthInMbps',
        serialization_name='baselineBandwidthInMbps',
        shape_name='BaselineBandwidthInMbps',
    ))

    baseline_throughput_in_mbps: BaselineThroughputInMBps | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BaselineThroughputInMBps',
        serialization_name='baselineThroughputInMBps',
        shape_name='BaselineThroughputInMBps',
    ))

    baseline_iops: BaselineIops | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BaselineIops',
        serialization_name='baselineIops',
        shape_name='BaselineIops',
    ))

    maximum_bandwidth_in_mbps: MaximumBandwidthInMbps | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaximumBandwidthInMbps',
        serialization_name='maximumBandwidthInMbps',
        shape_name='MaximumBandwidthInMbps',
    ))

    maximum_throughput_in_mbps: MaximumThroughputInMBps | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaximumThroughputInMBps',
        serialization_name='maximumThroughputInMBps',
        shape_name='MaximumThroughputInMBps',
    ))

    maximum_iops: MaximumIops | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaximumIops',
        serialization_name='maximumIops',
        shape_name='MaximumIops',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class EfaInfo(
    _base.Shape,
    shape_name='EfaInfo',
):
    maximum_efa_interfaces: MaximumEfaInterfaces | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaximumEfaInterfaces',
        serialization_name='maximumEfaInterfaces',
        shape_name='MaximumEfaInterfaces',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ElasticGpuAssociation(
    _base.Shape,
    shape_name='ElasticGpuAssociation',
):
    elastic_gpu_id: ElasticGpuId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticGpuId',
        serialization_name='elasticGpuId',
        shape_name='ElasticGpuId',
    ))

    elastic_gpu_association_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticGpuAssociationId',
        serialization_name='elasticGpuAssociationId',
        shape_name='String',
    ))

    elastic_gpu_association_state: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticGpuAssociationState',
        serialization_name='elasticGpuAssociationState',
        shape_name='String',
    ))

    elastic_gpu_association_time: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticGpuAssociationTime',
        serialization_name='elasticGpuAssociationTime',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ElasticGpuSpecification(
    _base.Shape,
    shape_name='ElasticGpuSpecification',
):
    type: str = _dc.field(metadata=_base.field_metadata(
        member_name='Type',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ElasticInferenceAccelerator(
    _base.Shape,
    shape_name='ElasticInferenceAccelerator',
):
    type: str = _dc.field(metadata=_base.field_metadata(
        member_name='Type',
        shape_name='String',
    ))

    count: ElasticInferenceAcceleratorCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Count',
        shape_name='ElasticInferenceAcceleratorCount',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ElasticInferenceAcceleratorAssociation(
    _base.Shape,
    shape_name='ElasticInferenceAcceleratorAssociation',
):
    elastic_inference_accelerator_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorArn',
        serialization_name='elasticInferenceAcceleratorArn',
        shape_name='String',
    ))

    elastic_inference_accelerator_association_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorAssociationId',
        serialization_name='elasticInferenceAcceleratorAssociationId',
        shape_name='String',
    ))

    elastic_inference_accelerator_association_state: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorAssociationState',
        serialization_name='elasticInferenceAcceleratorAssociationState',
        shape_name='String',
    ))

    elastic_inference_accelerator_association_time: _base.DateTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorAssociationTime',
        serialization_name='elasticInferenceAcceleratorAssociationTime',
        shape_name='DateTime',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class EnaSrdUdpSpecificationRequest(
    _base.Shape,
    shape_name='EnaSrdUdpSpecificationRequest',
):
    ena_srd_udp_enabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdUdpEnabled',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class EnclaveOptions(
    _base.Shape,
    shape_name='EnclaveOptions',
):
    enabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Enabled',
        serialization_name='enabled',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class EnclaveOptionsRequest(
    _base.Shape,
    shape_name='EnclaveOptionsRequest',
):
    enabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Enabled',
        shape_name='Boolean',
    ))


ExecutableByStringList: _ta.TypeAlias = _ta.Sequence[str]


@_dc.dataclass(frozen=True, kw_only=True)
class FpgaDeviceMemoryInfo(
    _base.Shape,
    shape_name='FpgaDeviceMemoryInfo',
):
    size_in_mi_b: FpgaDeviceMemorySize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SizeInMiB',
        serialization_name='sizeInMiB',
        shape_name='FpgaDeviceMemorySize',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class GpuDeviceMemoryInfo(
    _base.Shape,
    shape_name='GpuDeviceMemoryInfo',
):
    size_in_mi_b: GpuDeviceMemorySize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SizeInMiB',
        serialization_name='sizeInMiB',
        shape_name='GpuDeviceMemorySize',
    ))


GroupIdStringList: _ta.TypeAlias = _ta.Sequence[SecurityGroupId]


@_dc.dataclass(frozen=True, kw_only=True)
class GroupIdentifier(
    _base.Shape,
    shape_name='GroupIdentifier',
):
    group_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupId',
        serialization_name='groupId',
        shape_name='String',
    ))

    group_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupName',
        serialization_name='groupName',
        shape_name='String',
    ))


GroupNameStringList: _ta.TypeAlias = _ta.Sequence[SecurityGroupName]


@_dc.dataclass(frozen=True, kw_only=True)
class HibernationOptions(
    _base.Shape,
    shape_name='HibernationOptions',
):
    configured: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Configured',
        serialization_name='configured',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class HibernationOptionsRequest(
    _base.Shape,
    shape_name='HibernationOptionsRequest',
):
    configured: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Configured',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class IamInstanceProfile(
    _base.Shape,
    shape_name='IamInstanceProfile',
):
    arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Arn',
        serialization_name='arn',
        shape_name='String',
    ))

    id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Id',
        serialization_name='id',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class IamInstanceProfileSpecification(
    _base.Shape,
    shape_name='IamInstanceProfileSpecification',
):
    arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Arn',
        serialization_name='arn',
        shape_name='String',
    ))

    name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        serialization_name='name',
        shape_name='String',
    ))


ImageIdStringList: _ta.TypeAlias = _ta.Sequence[ImageId]


@_dc.dataclass(frozen=True, kw_only=True)
class InferenceDeviceMemoryInfo(
    _base.Shape,
    shape_name='InferenceDeviceMemoryInfo',
):
    size_in_mi_b: InferenceDeviceMemorySize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SizeInMiB',
        serialization_name='sizeInMiB',
        shape_name='InferenceDeviceMemorySize',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceAttachmentEnaSrdUdpSpecification(
    _base.Shape,
    shape_name='InstanceAttachmentEnaSrdUdpSpecification',
):
    ena_srd_udp_enabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdUdpEnabled',
        serialization_name='enaSrdUdpEnabled',
        shape_name='Boolean',
    ))


InstanceIdStringList: _ta.TypeAlias = _ta.Sequence[InstanceId]


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceIpv4Prefix(
    _base.Shape,
    shape_name='InstanceIpv4Prefix',
):
    ipv4_prefix: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv4Prefix',
        serialization_name='ipv4Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceIpv6Address(
    _base.Shape,
    shape_name='InstanceIpv6Address',
):
    ipv6_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Address',
        serialization_name='ipv6Address',
        shape_name='String',
    ))

    is_primary_ipv6: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IsPrimaryIpv6',
        serialization_name='isPrimaryIpv6',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceIpv6Prefix(
    _base.Shape,
    shape_name='InstanceIpv6Prefix',
):
    ipv6_prefix: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Prefix',
        serialization_name='ipv6Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceMaintenanceOptions(
    _base.Shape,
    shape_name='InstanceMaintenanceOptions',
):
    auto_recovery: InstanceAutoRecoveryState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AutoRecovery',
        serialization_name='autoRecovery',
        shape_name='InstanceAutoRecoveryState',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceMaintenanceOptionsRequest(
    _base.Shape,
    shape_name='InstanceMaintenanceOptionsRequest',
):
    auto_recovery: InstanceAutoRecoveryState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AutoRecovery',
        shape_name='InstanceAutoRecoveryState',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceMetadataOptionsRequest(
    _base.Shape,
    shape_name='InstanceMetadataOptionsRequest',
):
    http_tokens: HttpTokensState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HttpTokens',
        shape_name='HttpTokensState',
    ))

    http_put_response_hop_limit: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HttpPutResponseHopLimit',
        shape_name='Integer',
    ))

    http_endpoint: InstanceMetadataEndpointState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HttpEndpoint',
        shape_name='InstanceMetadataEndpointState',
    ))

    http_protocol_ipv6: InstanceMetadataProtocolState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HttpProtocolIpv6',
        shape_name='InstanceMetadataProtocolState',
    ))

    instance_metadata_tags: InstanceMetadataTagsState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceMetadataTags',
        shape_name='InstanceMetadataTagsState',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceMetadataOptionsResponse(
    _base.Shape,
    shape_name='InstanceMetadataOptionsResponse',
):
    state: InstanceMetadataOptionsState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='InstanceMetadataOptionsState',
    ))

    http_tokens: HttpTokensState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HttpTokens',
        serialization_name='httpTokens',
        shape_name='HttpTokensState',
    ))

    http_put_response_hop_limit: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HttpPutResponseHopLimit',
        serialization_name='httpPutResponseHopLimit',
        shape_name='Integer',
    ))

    http_endpoint: InstanceMetadataEndpointState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HttpEndpoint',
        serialization_name='httpEndpoint',
        shape_name='InstanceMetadataEndpointState',
    ))

    http_protocol_ipv6: InstanceMetadataProtocolState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HttpProtocolIpv6',
        serialization_name='httpProtocolIpv6',
        shape_name='InstanceMetadataProtocolState',
    ))

    instance_metadata_tags: InstanceMetadataTagsState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceMetadataTags',
        serialization_name='instanceMetadataTags',
        shape_name='InstanceMetadataTagsState',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceNetworkInterfaceAssociation(
    _base.Shape,
    shape_name='InstanceNetworkInterfaceAssociation',
):
    carrier_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CarrierIp',
        serialization_name='carrierIp',
        shape_name='String',
    ))

    customer_owned_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CustomerOwnedIp',
        serialization_name='customerOwnedIp',
        shape_name='String',
    ))

    ip_owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IpOwnerId',
        serialization_name='ipOwnerId',
        shape_name='String',
    ))

    public_dns_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicDnsName',
        serialization_name='publicDnsName',
        shape_name='String',
    ))

    public_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicIp',
        serialization_name='publicIp',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceNetworkPerformanceOptions(
    _base.Shape,
    shape_name='InstanceNetworkPerformanceOptions',
):
    bandwidth_weighting: InstanceBandwidthWeighting | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BandwidthWeighting',
        serialization_name='bandwidthWeighting',
        shape_name='InstanceBandwidthWeighting',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceNetworkPerformanceOptionsRequest(
    _base.Shape,
    shape_name='InstanceNetworkPerformanceOptionsRequest',
):
    bandwidth_weighting: InstanceBandwidthWeighting | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BandwidthWeighting',
        shape_name='InstanceBandwidthWeighting',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceState(
    _base.Shape,
    shape_name='InstanceState',
):
    code: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Code',
        serialization_name='code',
        shape_name='Integer',
    ))

    name: InstanceStateName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        serialization_name='name',
        shape_name='InstanceStateName',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InternetGatewayAttachment(
    _base.Shape,
    shape_name='InternetGatewayAttachment',
):
    state: AttachmentStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='AttachmentStatus',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))


InternetGatewayIdList: _ta.TypeAlias = _ta.Sequence[InternetGatewayId]


@_dc.dataclass(frozen=True, kw_only=True)
class IpRange(
    _base.Shape,
    shape_name='IpRange',
):
    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='description',
        shape_name='String',
    ))

    cidr_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CidrIp',
        serialization_name='cidrIp',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Ipv4PrefixSpecification(
    _base.Shape,
    shape_name='Ipv4PrefixSpecification',
):
    ipv4_prefix: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv4Prefix',
        serialization_name='ipv4Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Ipv4PrefixSpecificationRequest(
    _base.Shape,
    shape_name='Ipv4PrefixSpecificationRequest',
):
    ipv4_prefix: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv4Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Ipv6PrefixSpecification(
    _base.Shape,
    shape_name='Ipv6PrefixSpecification',
):
    ipv6_prefix: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Prefix',
        serialization_name='ipv6Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Ipv6PrefixSpecificationRequest(
    _base.Shape,
    shape_name='Ipv6PrefixSpecificationRequest',
):
    ipv6_prefix: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Ipv6Range(
    _base.Shape,
    shape_name='Ipv6Range',
):
    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='description',
        shape_name='String',
    ))

    cidr_ipv6: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CidrIpv6',
        serialization_name='cidrIpv6',
        shape_name='String',
    ))


KeyNameStringList: _ta.TypeAlias = _ta.Sequence[KeyPairName]

KeyPairIdStringList: _ta.TypeAlias = _ta.Sequence[KeyPairId]


@_dc.dataclass(frozen=True, kw_only=True)
class KeyPairInfo(
    _base.Shape,
    shape_name='KeyPairInfo',
):
    key_pair_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyPairId',
        serialization_name='keyPairId',
        shape_name='String',
    ))

    key_type: KeyType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyType',
        serialization_name='keyType',
        shape_name='KeyType',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    public_key: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicKey',
        serialization_name='publicKey',
        shape_name='String',
    ))

    create_time: _base.MillisecondDateTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CreateTime',
        serialization_name='createTime',
        shape_name='MillisecondDateTime',
    ))

    key_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyName',
        serialization_name='keyName',
        shape_name='String',
    ))

    key_fingerprint: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyFingerprint',
        serialization_name='keyFingerprint',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class LaunchTemplateSpecification(
    _base.Shape,
    shape_name='LaunchTemplateSpecification',
):
    launch_template_id: LaunchTemplateId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LaunchTemplateId',
        shape_name='LaunchTemplateId',
    ))

    launch_template_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LaunchTemplateName',
        shape_name='String',
    ))

    version: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Version',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class LicenseConfiguration(
    _base.Shape,
    shape_name='LicenseConfiguration',
):
    license_configuration_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LicenseConfigurationArn',
        serialization_name='licenseConfigurationArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class LicenseConfigurationRequest(
    _base.Shape,
    shape_name='LicenseConfigurationRequest',
):
    license_configuration_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LicenseConfigurationArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class MediaDeviceMemoryInfo(
    _base.Shape,
    shape_name='MediaDeviceMemoryInfo',
):
    size_in_mi_b: MediaDeviceMemorySize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SizeInMiB',
        serialization_name='sizeInMiB',
        shape_name='MediaDeviceMemorySize',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class MemoryInfo(
    _base.Shape,
    shape_name='MemoryInfo',
):
    size_in_mi_b: MemorySize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SizeInMiB',
        serialization_name='sizeInMiB',
        shape_name='MemorySize',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Monitoring(
    _base.Shape,
    shape_name='Monitoring',
):
    state: MonitoringState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='MonitoringState',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NetworkCardInfo(
    _base.Shape,
    shape_name='NetworkCardInfo',
):
    network_card_index: NetworkCardIndex | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkCardIndex',
        serialization_name='networkCardIndex',
        shape_name='NetworkCardIndex',
    ))

    network_performance: NetworkPerformance | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkPerformance',
        serialization_name='networkPerformance',
        shape_name='NetworkPerformance',
    ))

    maximum_network_interfaces: MaxNetworkInterfaces | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaximumNetworkInterfaces',
        serialization_name='maximumNetworkInterfaces',
        shape_name='MaxNetworkInterfaces',
    ))

    baseline_bandwidth_in_gbps: BaselineBandwidthInGbps | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BaselineBandwidthInGbps',
        serialization_name='baselineBandwidthInGbps',
        shape_name='BaselineBandwidthInGbps',
    ))

    peak_bandwidth_in_gbps: PeakBandwidthInGbps | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PeakBandwidthInGbps',
        serialization_name='peakBandwidthInGbps',
        shape_name='PeakBandwidthInGbps',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NetworkInterfaceAssociation(
    _base.Shape,
    shape_name='NetworkInterfaceAssociation',
):
    allocation_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AllocationId',
        serialization_name='allocationId',
        shape_name='String',
    ))

    association_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociationId',
        serialization_name='associationId',
        shape_name='String',
    ))

    ip_owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IpOwnerId',
        serialization_name='ipOwnerId',
        shape_name='String',
    ))

    public_dns_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicDnsName',
        serialization_name='publicDnsName',
        shape_name='String',
    ))

    public_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicIp',
        serialization_name='publicIp',
        shape_name='String',
    ))

    customer_owned_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CustomerOwnedIp',
        serialization_name='customerOwnedIp',
        shape_name='String',
    ))

    carrier_ip: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CarrierIp',
        serialization_name='carrierIp',
        shape_name='String',
    ))


NetworkInterfaceIdList: _ta.TypeAlias = _ta.Sequence[NetworkInterfaceId]


@_dc.dataclass(frozen=True, kw_only=True)
class NetworkInterfaceIpv6Address(
    _base.Shape,
    shape_name='NetworkInterfaceIpv6Address',
):
    ipv6_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Address',
        serialization_name='ipv6Address',
        shape_name='String',
    ))

    is_primary_ipv6: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IsPrimaryIpv6',
        serialization_name='isPrimaryIpv6',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NeuronDeviceCoreInfo(
    _base.Shape,
    shape_name='NeuronDeviceCoreInfo',
):
    count: NeuronDeviceCoreCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Count',
        serialization_name='count',
        shape_name='NeuronDeviceCoreCount',
    ))

    version: NeuronDeviceCoreVersion | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Version',
        serialization_name='version',
        shape_name='NeuronDeviceCoreVersion',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NeuronDeviceMemoryInfo(
    _base.Shape,
    shape_name='NeuronDeviceMemoryInfo',
):
    size_in_mi_b: NeuronDeviceMemorySize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SizeInMiB',
        serialization_name='sizeInMiB',
        shape_name='NeuronDeviceMemorySize',
    ))


NitroTpmSupportedVersionsList: _ta.TypeAlias = _ta.Sequence[NitroTpmSupportedVersionType]


@_dc.dataclass(frozen=True, kw_only=True)
class OperatorRequest(
    _base.Shape,
    shape_name='OperatorRequest',
):
    principal: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Principal',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class OperatorResponse(
    _base.Shape,
    shape_name='OperatorResponse',
):
    managed: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Managed',
        serialization_name='managed',
        shape_name='Boolean',
    ))

    principal: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Principal',
        serialization_name='principal',
        shape_name='String',
    ))


OwnerStringList: _ta.TypeAlias = _ta.Sequence[str]


@_dc.dataclass(frozen=True, kw_only=True)
class Placement(
    _base.Shape,
    shape_name='Placement',
):
    affinity: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Affinity',
        serialization_name='affinity',
        shape_name='String',
    ))

    group_name: PlacementGroupName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupName',
        serialization_name='groupName',
        shape_name='PlacementGroupName',
    ))

    partition_number: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PartitionNumber',
        serialization_name='partitionNumber',
        shape_name='Integer',
    ))

    host_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HostId',
        serialization_name='hostId',
        shape_name='String',
    ))

    tenancy: Tenancy | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tenancy',
        serialization_name='tenancy',
        shape_name='Tenancy',
    ))

    spread_domain: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SpreadDomain',
        serialization_name='spreadDomain',
        shape_name='String',
    ))

    host_resource_group_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HostResourceGroupArn',
        serialization_name='hostResourceGroupArn',
        shape_name='String',
    ))

    group_id: PlacementGroupId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupId',
        serialization_name='groupId',
        shape_name='PlacementGroupId',
    ))

    availability_zone: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AvailabilityZone',
        serialization_name='availabilityZone',
        shape_name='String',
    ))


PlacementGroupStrategyList: _ta.TypeAlias = _ta.Sequence[PlacementGroupStrategy]


@_dc.dataclass(frozen=True, kw_only=True)
class PrefixListId(
    _base.Shape,
    shape_name='PrefixListId',
):
    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='description',
        shape_name='String',
    ))

    prefix_list_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrefixListId',
        serialization_name='prefixListId',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class PrivateDnsNameOptionsOnLaunch(
    _base.Shape,
    shape_name='PrivateDnsNameOptionsOnLaunch',
):
    hostname_type: HostnameType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HostnameType',
        serialization_name='hostnameType',
        shape_name='HostnameType',
    ))

    enable_resource_name_dns_a_record: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsARecord',
        serialization_name='enableResourceNameDnsARecord',
        shape_name='Boolean',
    ))

    enable_resource_name_dns_aaaa_record: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsAAAARecord',
        serialization_name='enableResourceNameDnsAAAARecord',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class PrivateDnsNameOptionsRequest(
    _base.Shape,
    shape_name='PrivateDnsNameOptionsRequest',
):
    hostname_type: HostnameType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HostnameType',
        shape_name='HostnameType',
    ))

    enable_resource_name_dns_a_record: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsARecord',
        shape_name='Boolean',
    ))

    enable_resource_name_dns_aaaa_record: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsAAAARecord',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class PrivateDnsNameOptionsResponse(
    _base.Shape,
    shape_name='PrivateDnsNameOptionsResponse',
):
    hostname_type: HostnameType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HostnameType',
        serialization_name='hostnameType',
        shape_name='HostnameType',
    ))

    enable_resource_name_dns_a_record: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsARecord',
        serialization_name='enableResourceNameDnsARecord',
        shape_name='Boolean',
    ))

    enable_resource_name_dns_aaaa_record: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsAAAARecord',
        serialization_name='enableResourceNameDnsAAAARecord',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class PrivateIpAddressSpecification(
    _base.Shape,
    shape_name='PrivateIpAddressSpecification',
):
    primary: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Primary',
        serialization_name='primary',
        shape_name='Boolean',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class ProductCode(
    _base.Shape,
    shape_name='ProductCode',
):
    product_code_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ProductCodeId',
        serialization_name='productCode',
        shape_name='String',
    ))

    product_code_type: ProductCodeValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ProductCodeType',
        serialization_name='type',
        shape_name='ProductCodeValues',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class PropagatingVgw(
    _base.Shape,
    shape_name='PropagatingVgw',
):
    gateway_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GatewayId',
        serialization_name='gatewayId',
        shape_name='String',
    ))


PublicIpStringList: _ta.TypeAlias = _ta.Sequence[str]

RequestInstanceTypeList: _ta.TypeAlias = _ta.Sequence[InstanceType]

RootDeviceTypeList: _ta.TypeAlias = _ta.Sequence[RootDeviceType]


@_dc.dataclass(frozen=True, kw_only=True)
class Route(
    _base.Shape,
    shape_name='Route',
):
    destination_cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationCidrBlock',
        serialization_name='destinationCidrBlock',
        shape_name='String',
    ))

    destination_ipv6_cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationIpv6CidrBlock',
        serialization_name='destinationIpv6CidrBlock',
        shape_name='String',
    ))

    destination_prefix_list_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DestinationPrefixListId',
        serialization_name='destinationPrefixListId',
        shape_name='String',
    ))

    egress_only_internet_gateway_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EgressOnlyInternetGatewayId',
        serialization_name='egressOnlyInternetGatewayId',
        shape_name='String',
    ))

    gateway_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GatewayId',
        serialization_name='gatewayId',
        shape_name='String',
    ))

    instance_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceId',
        serialization_name='instanceId',
        shape_name='String',
    ))

    instance_owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceOwnerId',
        serialization_name='instanceOwnerId',
        shape_name='String',
    ))

    nat_gateway_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NatGatewayId',
        serialization_name='natGatewayId',
        shape_name='String',
    ))

    transit_gateway_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TransitGatewayId',
        serialization_name='transitGatewayId',
        shape_name='String',
    ))

    local_gateway_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LocalGatewayId',
        serialization_name='localGatewayId',
        shape_name='String',
    ))

    carrier_gateway_id: CarrierGatewayId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CarrierGatewayId',
        serialization_name='carrierGatewayId',
        shape_name='CarrierGatewayId',
    ))

    network_interface_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        serialization_name='networkInterfaceId',
        shape_name='String',
    ))

    origin: RouteOrigin | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Origin',
        serialization_name='origin',
        shape_name='RouteOrigin',
    ))

    state: RouteState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='RouteState',
    ))

    vpc_peering_connection_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcPeeringConnectionId',
        serialization_name='vpcPeeringConnectionId',
        shape_name='String',
    ))

    core_network_arn: CoreNetworkArn | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CoreNetworkArn',
        serialization_name='coreNetworkArn',
        shape_name='CoreNetworkArn',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class RouteTableAssociationState(
    _base.Shape,
    shape_name='RouteTableAssociationState',
):
    state: RouteTableAssociationStateCode | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='RouteTableAssociationStateCode',
    ))

    status_message: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StatusMessage',
        serialization_name='statusMessage',
        shape_name='String',
    ))


RouteTableIdStringList: _ta.TypeAlias = _ta.Sequence[RouteTableId]


@_dc.dataclass(frozen=True, kw_only=True)
class RunInstancesMonitoringEnabled(
    _base.Shape,
    shape_name='RunInstancesMonitoringEnabled',
):
    enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Enabled',
        serialization_name='enabled',
        shape_name='Boolean',
    ))


SecurityGroupIdStringList: _ta.TypeAlias = _ta.Sequence[SecurityGroupId]

SecurityGroupStringList: _ta.TypeAlias = _ta.Sequence[SecurityGroupName]


@_dc.dataclass(frozen=True, kw_only=True)
class SpotMarketOptions(
    _base.Shape,
    shape_name='SpotMarketOptions',
):
    max_price: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxPrice',
        shape_name='String',
    ))

    spot_instance_type: SpotInstanceType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SpotInstanceType',
        shape_name='SpotInstanceType',
    ))

    block_duration_minutes: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BlockDurationMinutes',
        shape_name='Integer',
    ))

    valid_until: _base.DateTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ValidUntil',
        shape_name='DateTime',
    ))

    instance_interruption_behavior: InstanceInterruptionBehavior | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceInterruptionBehavior',
        shape_name='InstanceInterruptionBehavior',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class StateReason(
    _base.Shape,
    shape_name='StateReason',
):
    code: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Code',
        serialization_name='code',
        shape_name='String',
    ))

    message: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Message',
        serialization_name='message',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class SubnetCidrBlockState(
    _base.Shape,
    shape_name='SubnetCidrBlockState',
):
    state: SubnetCidrBlockStateCode | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='SubnetCidrBlockStateCode',
    ))

    status_message: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StatusMessage',
        serialization_name='statusMessage',
        shape_name='String',
    ))


SubnetIdStringList: _ta.TypeAlias = _ta.Sequence[SubnetId]

SupportedAdditionalProcessorFeatureList: _ta.TypeAlias = _ta.Sequence[SupportedAdditionalProcessorFeature]


@_dc.dataclass(frozen=True, kw_only=True)
class TagSpecification(
    _base.Shape,
    shape_name='TagSpecification',
):
    resource_type: ResourceType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ResourceType',
        serialization_name='resourceType',
        shape_name='ResourceType',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='Tag',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))


ThreadsPerCoreList: _ta.TypeAlias = _ta.Sequence[ThreadsPerCore]

UsageClassTypeList: _ta.TypeAlias = _ta.Sequence[UsageClassType]


@_dc.dataclass(frozen=True, kw_only=True)
class UserIdGroupPair(
    _base.Shape,
    shape_name='UserIdGroupPair',
):
    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='description',
        shape_name='String',
    ))

    user_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UserId',
        serialization_name='userId',
        shape_name='String',
    ))

    group_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupName',
        serialization_name='groupName',
        shape_name='String',
    ))

    group_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupId',
        serialization_name='groupId',
        shape_name='String',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))

    vpc_peering_connection_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcPeeringConnectionId',
        serialization_name='vpcPeeringConnectionId',
        shape_name='String',
    ))

    peering_status: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PeeringStatus',
        serialization_name='peeringStatus',
        shape_name='String',
    ))


ValueStringList: _ta.TypeAlias = _ta.Sequence[str]

VirtualizationTypeList: _ta.TypeAlias = _ta.Sequence[VirtualizationType]


@_dc.dataclass(frozen=True, kw_only=True)
class VpcCidrBlockState(
    _base.Shape,
    shape_name='VpcCidrBlockState',
):
    state: VpcCidrBlockStateCode | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='VpcCidrBlockStateCode',
    ))

    status_message: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StatusMessage',
        serialization_name='statusMessage',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class VpcEncryptionControlExclusion(
    _base.Shape,
    shape_name='VpcEncryptionControlExclusion',
):
    state: VpcEncryptionControlExclusionState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='VpcEncryptionControlExclusionState',
    ))

    state_message: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StateMessage',
        serialization_name='stateMessage',
        shape_name='String',
    ))


VpcIdStringList: _ta.TypeAlias = _ta.Sequence[VpcId]

AddressList: _ta.TypeAlias = _ta.Sequence[Address]


@_dc.dataclass(frozen=True, kw_only=True)
class AttachmentEnaSrdSpecification(
    _base.Shape,
    shape_name='AttachmentEnaSrdSpecification',
):
    ena_srd_enabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdEnabled',
        serialization_name='enaSrdEnabled',
        shape_name='Boolean',
    ))

    ena_srd_udp_specification: AttachmentEnaSrdUdpSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdUdpSpecification',
        serialization_name='enaSrdUdpSpecification',
        shape_name='AttachmentEnaSrdUdpSpecification',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class BlockDeviceMapping(
    _base.Shape,
    shape_name='BlockDeviceMapping',
):
    ebs: EbsBlockDevice | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ebs',
        serialization_name='ebs',
        shape_name='EbsBlockDevice',
    ))

    no_device: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NoDevice',
        serialization_name='noDevice',
        shape_name='String',
    ))

    device_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeviceName',
        serialization_name='deviceName',
        shape_name='String',
    ))

    virtual_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VirtualName',
        serialization_name='virtualName',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CapacityReservationSpecification(
    _base.Shape,
    shape_name='CapacityReservationSpecification',
):
    capacity_reservation_preference: CapacityReservationPreference | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationPreference',
        shape_name='CapacityReservationPreference',
    ))

    capacity_reservation_target: CapacityReservationTarget | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationTarget',
        shape_name='CapacityReservationTarget',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CapacityReservationSpecificationResponse(
    _base.Shape,
    shape_name='CapacityReservationSpecificationResponse',
):
    capacity_reservation_preference: CapacityReservationPreference | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationPreference',
        serialization_name='capacityReservationPreference',
        shape_name='CapacityReservationPreference',
    ))

    capacity_reservation_target: CapacityReservationTargetResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationTarget',
        serialization_name='capacityReservationTarget',
        shape_name='CapacityReservationTargetResponse',
    ))


DiskInfoList: _ta.TypeAlias = _ta.Sequence[DiskInfo]


@_dc.dataclass(frozen=True, kw_only=True)
class EbsInfo(
    _base.Shape,
    shape_name='EbsInfo',
):
    ebs_optimized_support: EbsOptimizedSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EbsOptimizedSupport',
        serialization_name='ebsOptimizedSupport',
        shape_name='EbsOptimizedSupport',
    ))

    encryption_support: EbsEncryptionSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EncryptionSupport',
        serialization_name='encryptionSupport',
        shape_name='EbsEncryptionSupport',
    ))

    ebs_optimized_info: EbsOptimizedInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EbsOptimizedInfo',
        serialization_name='ebsOptimizedInfo',
        shape_name='EbsOptimizedInfo',
    ))

    nvme_support: EbsNvmeSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NvmeSupport',
        serialization_name='nvmeSupport',
        shape_name='EbsNvmeSupport',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class EbsInstanceBlockDevice(
    _base.Shape,
    shape_name='EbsInstanceBlockDevice',
):
    attach_time: _base.DateTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AttachTime',
        serialization_name='attachTime',
        shape_name='DateTime',
    ))

    delete_on_termination: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        serialization_name='deleteOnTermination',
        shape_name='Boolean',
    ))

    status: AttachmentStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Status',
        serialization_name='status',
        shape_name='AttachmentStatus',
    ))

    volume_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VolumeId',
        serialization_name='volumeId',
        shape_name='String',
    ))

    associated_resource: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociatedResource',
        serialization_name='associatedResource',
        shape_name='String',
    ))

    volume_owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VolumeOwnerId',
        serialization_name='volumeOwnerId',
        shape_name='String',
    ))

    operator: OperatorResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Operator',
        serialization_name='operator',
        shape_name='OperatorResponse',
    ))


ElasticGpuAssociationList: _ta.TypeAlias = _ta.Sequence[ElasticGpuAssociation]

ElasticGpuSpecifications: _ta.TypeAlias = _ta.Sequence[ElasticGpuSpecification]

ElasticInferenceAcceleratorAssociationList: _ta.TypeAlias = _ta.Sequence[ElasticInferenceAcceleratorAssociation]

ElasticInferenceAccelerators: _ta.TypeAlias = _ta.Sequence[ElasticInferenceAccelerator]


@_dc.dataclass(frozen=True, kw_only=True)
class EnaSrdSpecificationRequest(
    _base.Shape,
    shape_name='EnaSrdSpecificationRequest',
):
    ena_srd_enabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdEnabled',
        shape_name='Boolean',
    ))

    ena_srd_udp_specification: EnaSrdUdpSpecificationRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdUdpSpecification',
        shape_name='EnaSrdUdpSpecificationRequest',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Filter(
    _base.Shape,
    shape_name='Filter',
):
    name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        shape_name='String',
    ))

    values: ValueStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Values',
        serialization_name='Value',
        value_type=_base.ListValueType(str),
        shape_name='ValueStringList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class FpgaDeviceInfo(
    _base.Shape,
    shape_name='FpgaDeviceInfo',
):
    name: FpgaDeviceName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        serialization_name='name',
        shape_name='FpgaDeviceName',
    ))

    manufacturer: FpgaDeviceManufacturerName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Manufacturer',
        serialization_name='manufacturer',
        shape_name='FpgaDeviceManufacturerName',
    ))

    count: FpgaDeviceCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Count',
        serialization_name='count',
        shape_name='FpgaDeviceCount',
    ))

    memory_info: FpgaDeviceMemoryInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MemoryInfo',
        serialization_name='memoryInfo',
        shape_name='FpgaDeviceMemoryInfo',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class GpuDeviceInfo(
    _base.Shape,
    shape_name='GpuDeviceInfo',
):
    name: GpuDeviceName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        serialization_name='name',
        shape_name='GpuDeviceName',
    ))

    manufacturer: GpuDeviceManufacturerName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Manufacturer',
        serialization_name='manufacturer',
        shape_name='GpuDeviceManufacturerName',
    ))

    count: GpuDeviceCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Count',
        serialization_name='count',
        shape_name='GpuDeviceCount',
    ))

    memory_info: GpuDeviceMemoryInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MemoryInfo',
        serialization_name='memoryInfo',
        shape_name='GpuDeviceMemoryInfo',
    ))


GroupIdentifierList: _ta.TypeAlias = _ta.Sequence[GroupIdentifier]


@_dc.dataclass(frozen=True, kw_only=True)
class InferenceDeviceInfo(
    _base.Shape,
    shape_name='InferenceDeviceInfo',
):
    count: InferenceDeviceCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Count',
        serialization_name='count',
        shape_name='InferenceDeviceCount',
    ))

    name: InferenceDeviceName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        serialization_name='name',
        shape_name='InferenceDeviceName',
    ))

    manufacturer: InferenceDeviceManufacturerName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Manufacturer',
        serialization_name='manufacturer',
        shape_name='InferenceDeviceManufacturerName',
    ))

    memory_info: InferenceDeviceMemoryInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MemoryInfo',
        serialization_name='memoryInfo',
        shape_name='InferenceDeviceMemoryInfo',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceAttachmentEnaSrdSpecification(
    _base.Shape,
    shape_name='InstanceAttachmentEnaSrdSpecification',
):
    ena_srd_enabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdEnabled',
        serialization_name='enaSrdEnabled',
        shape_name='Boolean',
    ))

    ena_srd_udp_specification: InstanceAttachmentEnaSrdUdpSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdUdpSpecification',
        serialization_name='enaSrdUdpSpecification',
        shape_name='InstanceAttachmentEnaSrdUdpSpecification',
    ))


InstanceIpv4PrefixList: _ta.TypeAlias = _ta.Sequence[InstanceIpv4Prefix]

InstanceIpv6AddressList: _ta.TypeAlias = _ta.Sequence[InstanceIpv6Address]

InstanceIpv6PrefixList: _ta.TypeAlias = _ta.Sequence[InstanceIpv6Prefix]


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceMarketOptionsRequest(
    _base.Shape,
    shape_name='InstanceMarketOptionsRequest',
):
    market_type: MarketType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MarketType',
        shape_name='MarketType',
    ))

    spot_options: SpotMarketOptions | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SpotOptions',
        shape_name='SpotMarketOptions',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstancePrivateIpAddress(
    _base.Shape,
    shape_name='InstancePrivateIpAddress',
):
    association: InstanceNetworkInterfaceAssociation | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Association',
        serialization_name='association',
        shape_name='InstanceNetworkInterfaceAssociation',
    ))

    primary: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Primary',
        serialization_name='primary',
        shape_name='Boolean',
    ))

    private_dns_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        serialization_name='privateDnsName',
        shape_name='String',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceStateChange(
    _base.Shape,
    shape_name='InstanceStateChange',
):
    instance_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceId',
        serialization_name='instanceId',
        shape_name='String',
    ))

    current_state: InstanceState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CurrentState',
        serialization_name='currentState',
        shape_name='InstanceState',
    ))

    previous_state: InstanceState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PreviousState',
        serialization_name='previousState',
        shape_name='InstanceState',
    ))


InternetGatewayAttachmentList: _ta.TypeAlias = _ta.Sequence[InternetGatewayAttachment]

IpRangeList: _ta.TypeAlias = _ta.Sequence[IpRange]

Ipv4PrefixList: _ta.TypeAlias = _ta.Sequence[Ipv4PrefixSpecificationRequest]

Ipv4PrefixesList: _ta.TypeAlias = _ta.Sequence[Ipv4PrefixSpecification]

Ipv6PrefixList: _ta.TypeAlias = _ta.Sequence[Ipv6PrefixSpecificationRequest]

Ipv6PrefixesList: _ta.TypeAlias = _ta.Sequence[Ipv6PrefixSpecification]

Ipv6RangeList: _ta.TypeAlias = _ta.Sequence[Ipv6Range]

KeyPairList: _ta.TypeAlias = _ta.Sequence[KeyPairInfo]

LicenseList: _ta.TypeAlias = _ta.Sequence[LicenseConfiguration]

LicenseSpecificationListRequest: _ta.TypeAlias = _ta.Sequence[LicenseConfigurationRequest]


@_dc.dataclass(frozen=True, kw_only=True)
class MediaDeviceInfo(
    _base.Shape,
    shape_name='MediaDeviceInfo',
):
    count: MediaDeviceCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Count',
        serialization_name='count',
        shape_name='MediaDeviceCount',
    ))

    name: MediaDeviceName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        serialization_name='name',
        shape_name='MediaDeviceName',
    ))

    manufacturer: MediaDeviceManufacturerName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Manufacturer',
        serialization_name='manufacturer',
        shape_name='MediaDeviceManufacturerName',
    ))

    memory_info: MediaDeviceMemoryInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MemoryInfo',
        serialization_name='memoryInfo',
        shape_name='MediaDeviceMemoryInfo',
    ))


NetworkCardInfoList: _ta.TypeAlias = _ta.Sequence[NetworkCardInfo]

NetworkInterfaceIpv6AddressesList: _ta.TypeAlias = _ta.Sequence[NetworkInterfaceIpv6Address]


@_dc.dataclass(frozen=True, kw_only=True)
class NetworkInterfacePrivateIpAddress(
    _base.Shape,
    shape_name='NetworkInterfacePrivateIpAddress',
):
    association: NetworkInterfaceAssociation | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Association',
        serialization_name='association',
        shape_name='NetworkInterfaceAssociation',
    ))

    primary: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Primary',
        serialization_name='primary',
        shape_name='Boolean',
    ))

    private_dns_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        serialization_name='privateDnsName',
        shape_name='String',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NeuronDeviceInfo(
    _base.Shape,
    shape_name='NeuronDeviceInfo',
):
    count: NeuronDeviceCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Count',
        serialization_name='count',
        shape_name='NeuronDeviceCount',
    ))

    name: NeuronDeviceName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        serialization_name='name',
        shape_name='NeuronDeviceName',
    ))

    core_info: NeuronDeviceCoreInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CoreInfo',
        serialization_name='coreInfo',
        shape_name='NeuronDeviceCoreInfo',
    ))

    memory_info: NeuronDeviceMemoryInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MemoryInfo',
        serialization_name='memoryInfo',
        shape_name='NeuronDeviceMemoryInfo',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NitroTpmInfo(
    _base.Shape,
    shape_name='NitroTpmInfo',
):
    supported_versions: NitroTpmSupportedVersionsList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SupportedVersions',
        serialization_name='supportedVersions',
        value_type=_base.ListValueType(NitroTpmSupportedVersionType),
        shape_name='NitroTpmSupportedVersionsList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class PlacementGroupInfo(
    _base.Shape,
    shape_name='PlacementGroupInfo',
):
    supported_strategies: PlacementGroupStrategyList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SupportedStrategies',
        serialization_name='supportedStrategies',
        value_type=_base.ListValueType(PlacementGroupStrategy),
        shape_name='PlacementGroupStrategyList',
    ))


PrefixListIdList: _ta.TypeAlias = _ta.Sequence[PrefixListId]

PrivateIpAddressSpecificationList: _ta.TypeAlias = _ta.Sequence[PrivateIpAddressSpecification]


@_dc.dataclass(frozen=True, kw_only=True)
class ProcessorInfo(
    _base.Shape,
    shape_name='ProcessorInfo',
):
    supported_architectures: ArchitectureTypeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SupportedArchitectures',
        serialization_name='supportedArchitectures',
        value_type=_base.ListValueType(ArchitectureType),
        shape_name='ArchitectureTypeList',
    ))

    sustained_clock_speed_in_ghz: ProcessorSustainedClockSpeed | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SustainedClockSpeedInGhz',
        serialization_name='sustainedClockSpeedInGhz',
        shape_name='ProcessorSustainedClockSpeed',
    ))

    supported_features: SupportedAdditionalProcessorFeatureList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SupportedFeatures',
        serialization_name='supportedFeatures',
        value_type=_base.ListValueType(SupportedAdditionalProcessorFeature),
        shape_name='SupportedAdditionalProcessorFeatureList',
    ))

    manufacturer: CpuManufacturerName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Manufacturer',
        serialization_name='manufacturer',
        shape_name='CpuManufacturerName',
    ))


ProductCodeList: _ta.TypeAlias = _ta.Sequence[ProductCode]

PropagatingVgwList: _ta.TypeAlias = _ta.Sequence[PropagatingVgw]


@_dc.dataclass(frozen=True, kw_only=True)
class RebootInstancesRequest(
    _base.Shape,
    shape_name='RebootInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        serialization_name='InstanceId',
        value_type=_base.ListValueType(InstanceId),
        shape_name='InstanceIdStringList',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))


RouteList: _ta.TypeAlias = _ta.Sequence[Route]


@_dc.dataclass(frozen=True, kw_only=True)
class RouteTableAssociation(
    _base.Shape,
    shape_name='RouteTableAssociation',
):
    main: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Main',
        serialization_name='main',
        shape_name='Boolean',
    ))

    route_table_association_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RouteTableAssociationId',
        serialization_name='routeTableAssociationId',
        shape_name='String',
    ))

    route_table_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RouteTableId',
        serialization_name='routeTableId',
        shape_name='String',
    ))

    subnet_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetId',
        serialization_name='subnetId',
        shape_name='String',
    ))

    gateway_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GatewayId',
        serialization_name='gatewayId',
        shape_name='String',
    ))

    association_state: RouteTableAssociationState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociationState',
        serialization_name='associationState',
        shape_name='RouteTableAssociationState',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class StartInstancesRequest(
    _base.Shape,
    shape_name='StartInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        serialization_name='InstanceId',
        value_type=_base.ListValueType(InstanceId),
        shape_name='InstanceIdStringList',
    ))

    additional_info: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AdditionalInfo',
        serialization_name='additionalInfo',
        shape_name='String',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class StopInstancesRequest(
    _base.Shape,
    shape_name='StopInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        serialization_name='InstanceId',
        value_type=_base.ListValueType(InstanceId),
        shape_name='InstanceIdStringList',
    ))

    hibernate: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Hibernate',
        shape_name='Boolean',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    force: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Force',
        serialization_name='force',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class SubnetIpv6CidrBlockAssociation(
    _base.Shape,
    shape_name='SubnetIpv6CidrBlockAssociation',
):
    association_id: SubnetCidrAssociationId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociationId',
        serialization_name='associationId',
        shape_name='SubnetCidrAssociationId',
    ))

    ipv6_cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6CidrBlock',
        serialization_name='ipv6CidrBlock',
        shape_name='String',
    ))

    ipv6_cidr_block_state: SubnetCidrBlockState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6CidrBlockState',
        serialization_name='ipv6CidrBlockState',
        shape_name='SubnetCidrBlockState',
    ))

    ipv6_address_attribute: Ipv6AddressAttribute | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6AddressAttribute',
        serialization_name='ipv6AddressAttribute',
        shape_name='Ipv6AddressAttribute',
    ))

    ip_source: IpSource | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IpSource',
        serialization_name='ipSource',
        shape_name='IpSource',
    ))


TagSpecificationList: _ta.TypeAlias = _ta.Sequence[TagSpecification]


@_dc.dataclass(frozen=True, kw_only=True)
class TerminateInstancesRequest(
    _base.Shape,
    shape_name='TerminateInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        serialization_name='InstanceId',
        value_type=_base.ListValueType(InstanceId),
        shape_name='InstanceIdStringList',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))


UserIdGroupPairList: _ta.TypeAlias = _ta.Sequence[UserIdGroupPair]


@_dc.dataclass(frozen=True, kw_only=True)
class VCpuInfo(
    _base.Shape,
    shape_name='VCpuInfo',
):
    default_v_cpus: VCpuCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DefaultVCpus',
        serialization_name='defaultVCpus',
        shape_name='VCpuCount',
    ))

    default_cores: CoreCount | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DefaultCores',
        serialization_name='defaultCores',
        shape_name='CoreCount',
    ))

    default_threads_per_core: ThreadsPerCore | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DefaultThreadsPerCore',
        serialization_name='defaultThreadsPerCore',
        shape_name='ThreadsPerCore',
    ))

    valid_cores: CoreCountList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ValidCores',
        serialization_name='validCores',
        value_type=_base.ListValueType(CoreCount),
        shape_name='CoreCountList',
    ))

    valid_threads_per_core: ThreadsPerCoreList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ValidThreadsPerCore',
        serialization_name='validThreadsPerCore',
        value_type=_base.ListValueType(ThreadsPerCore),
        shape_name='ThreadsPerCoreList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class VpcCidrBlockAssociation(
    _base.Shape,
    shape_name='VpcCidrBlockAssociation',
):
    association_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociationId',
        serialization_name='associationId',
        shape_name='String',
    ))

    cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CidrBlock',
        serialization_name='cidrBlock',
        shape_name='String',
    ))

    cidr_block_state: VpcCidrBlockState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CidrBlockState',
        serialization_name='cidrBlockState',
        shape_name='VpcCidrBlockState',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class VpcEncryptionControlExclusions(
    _base.Shape,
    shape_name='VpcEncryptionControlExclusions',
):
    internet_gateway: VpcEncryptionControlExclusion | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InternetGateway',
        serialization_name='internetGateway',
        shape_name='VpcEncryptionControlExclusion',
    ))

    egress_only_internet_gateway: VpcEncryptionControlExclusion | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EgressOnlyInternetGateway',
        serialization_name='egressOnlyInternetGateway',
        shape_name='VpcEncryptionControlExclusion',
    ))

    nat_gateway: VpcEncryptionControlExclusion | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NatGateway',
        serialization_name='natGateway',
        shape_name='VpcEncryptionControlExclusion',
    ))

    virtual_private_gateway: VpcEncryptionControlExclusion | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VirtualPrivateGateway',
        serialization_name='virtualPrivateGateway',
        shape_name='VpcEncryptionControlExclusion',
    ))

    vpc_peering: VpcEncryptionControlExclusion | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcPeering',
        serialization_name='vpcPeering',
        shape_name='VpcEncryptionControlExclusion',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class VpcIpv6CidrBlockAssociation(
    _base.Shape,
    shape_name='VpcIpv6CidrBlockAssociation',
):
    association_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociationId',
        serialization_name='associationId',
        shape_name='String',
    ))

    ipv6_cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6CidrBlock',
        serialization_name='ipv6CidrBlock',
        shape_name='String',
    ))

    ipv6_cidr_block_state: VpcCidrBlockState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6CidrBlockState',
        serialization_name='ipv6CidrBlockState',
        shape_name='VpcCidrBlockState',
    ))

    network_border_group: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkBorderGroup',
        serialization_name='networkBorderGroup',
        shape_name='String',
    ))

    ipv6_pool: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Pool',
        serialization_name='ipv6Pool',
        shape_name='String',
    ))

    ipv6_address_attribute: Ipv6AddressAttribute | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6AddressAttribute',
        serialization_name='ipv6AddressAttribute',
        shape_name='Ipv6AddressAttribute',
    ))

    ip_source: IpSource | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IpSource',
        serialization_name='ipSource',
        shape_name='IpSource',
    ))


BlockDeviceMappingList: _ta.TypeAlias = _ta.Sequence[BlockDeviceMapping]

BlockDeviceMappingRequestList: _ta.TypeAlias = _ta.Sequence[BlockDeviceMapping]


@_dc.dataclass(frozen=True, kw_only=True)
class CreateRouteTableRequest(
    _base.Shape,
    shape_name='CreateRouteTableRequest',
):
    tag_specifications: TagSpecificationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TagSpecifications',
        serialization_name='TagSpecification',
        value_type=_base.ListValueType(TagSpecification),
        shape_name='TagSpecificationList',
    ))

    client_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ClientToken',
        shape_name='String',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    vpc_id: VpcId = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='VpcId',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CreateSecurityGroupRequest(
    _base.Shape,
    shape_name='CreateSecurityGroupRequest',
):
    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='GroupDescription',
        shape_name='String',
    ))

    group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='GroupName',
        shape_name='String',
    ))

    vpc_id: VpcId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='VpcId',
    ))

    tag_specifications: TagSpecificationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TagSpecifications',
        serialization_name='TagSpecification',
        value_type=_base.ListValueType(TagSpecification),
        shape_name='TagSpecificationList',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeAddressesResult(
    _base.Shape,
    shape_name='DescribeAddressesResult',
):
    addresses: AddressList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Addresses',
        serialization_name='addressesSet',
        value_type=_base.ListValueType(Address),
        shape_name='AddressList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeKeyPairsResult(
    _base.Shape,
    shape_name='DescribeKeyPairsResult',
):
    key_pairs: KeyPairList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyPairs',
        serialization_name='keySet',
        value_type=_base.ListValueType(KeyPairInfo),
        shape_name='KeyPairList',
    ))


FilterList: _ta.TypeAlias = _ta.Sequence[Filter]

FpgaDeviceInfoList: _ta.TypeAlias = _ta.Sequence[FpgaDeviceInfo]

GpuDeviceInfoList: _ta.TypeAlias = _ta.Sequence[GpuDeviceInfo]

InferenceDeviceInfoList: _ta.TypeAlias = _ta.Sequence[InferenceDeviceInfo]


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceBlockDeviceMapping(
    _base.Shape,
    shape_name='InstanceBlockDeviceMapping',
):
    device_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeviceName',
        serialization_name='deviceName',
        shape_name='String',
    ))

    ebs: EbsInstanceBlockDevice | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ebs',
        serialization_name='ebs',
        shape_name='EbsInstanceBlockDevice',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceNetworkInterfaceAttachment(
    _base.Shape,
    shape_name='InstanceNetworkInterfaceAttachment',
):
    attach_time: _base.DateTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AttachTime',
        serialization_name='attachTime',
        shape_name='DateTime',
    ))

    attachment_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AttachmentId',
        serialization_name='attachmentId',
        shape_name='String',
    ))

    delete_on_termination: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        serialization_name='deleteOnTermination',
        shape_name='Boolean',
    ))

    device_index: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeviceIndex',
        serialization_name='deviceIndex',
        shape_name='Integer',
    ))

    status: AttachmentStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Status',
        serialization_name='status',
        shape_name='AttachmentStatus',
    ))

    network_card_index: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkCardIndex',
        serialization_name='networkCardIndex',
        shape_name='Integer',
    ))

    ena_srd_specification: InstanceAttachmentEnaSrdSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdSpecification',
        serialization_name='enaSrdSpecification',
        shape_name='InstanceAttachmentEnaSrdSpecification',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceNetworkInterfaceSpecification(
    _base.Shape,
    shape_name='InstanceNetworkInterfaceSpecification',
):
    associate_public_ip_address: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociatePublicIpAddress',
        serialization_name='associatePublicIpAddress',
        shape_name='Boolean',
    ))

    delete_on_termination: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        serialization_name='deleteOnTermination',
        shape_name='Boolean',
    ))

    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='description',
        shape_name='String',
    ))

    device_index: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeviceIndex',
        serialization_name='deviceIndex',
        shape_name='Integer',
    ))

    groups: SecurityGroupIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Groups',
        serialization_name='SecurityGroupId',
        value_type=_base.ListValueType(SecurityGroupId),
        shape_name='SecurityGroupIdStringList',
    ))

    ipv6_address_count: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6AddressCount',
        serialization_name='ipv6AddressCount',
        shape_name='Integer',
    ))

    ipv6_addresses: InstanceIpv6AddressList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Addresses',
        serialization_name='ipv6AddressesSet',
        value_type=_base.ListValueType(InstanceIpv6Address),
        shape_name='InstanceIpv6AddressList',
    ))

    network_interface_id: NetworkInterfaceId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        serialization_name='networkInterfaceId',
        shape_name='NetworkInterfaceId',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))

    private_ip_addresses: PrivateIpAddressSpecificationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddresses',
        serialization_name='privateIpAddressesSet',
        value_type=_base.ListValueType(PrivateIpAddressSpecification),
        shape_name='PrivateIpAddressSpecificationList',
    ))

    secondary_private_ip_address_count: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SecondaryPrivateIpAddressCount',
        serialization_name='secondaryPrivateIpAddressCount',
        shape_name='Integer',
    ))

    subnet_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetId',
        serialization_name='subnetId',
        shape_name='String',
    ))

    associate_carrier_ip_address: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssociateCarrierIpAddress',
        shape_name='Boolean',
    ))

    interface_type: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InterfaceType',
        shape_name='String',
    ))

    network_card_index: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkCardIndex',
        shape_name='Integer',
    ))

    ipv4_prefixes: Ipv4PrefixList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv4Prefixes',
        serialization_name='Ipv4Prefix',
        value_type=_base.ListValueType(Ipv4PrefixSpecificationRequest),
        shape_name='Ipv4PrefixList',
    ))

    ipv4_prefix_count: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv4PrefixCount',
        shape_name='Integer',
    ))

    ipv6_prefixes: Ipv6PrefixList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Prefixes',
        serialization_name='Ipv6Prefix',
        value_type=_base.ListValueType(Ipv6PrefixSpecificationRequest),
        shape_name='Ipv6PrefixList',
    ))

    ipv6_prefix_count: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6PrefixCount',
        shape_name='Integer',
    ))

    primary_ipv6: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrimaryIpv6',
        shape_name='Boolean',
    ))

    ena_srd_specification: EnaSrdSpecificationRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdSpecification',
        shape_name='EnaSrdSpecificationRequest',
    ))

    connection_tracking_specification: ConnectionTrackingSpecificationRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ConnectionTrackingSpecification',
        shape_name='ConnectionTrackingSpecificationRequest',
    ))


InstancePrivateIpAddressList: _ta.TypeAlias = _ta.Sequence[InstancePrivateIpAddress]

InstanceStateChangeList: _ta.TypeAlias = _ta.Sequence[InstanceStateChange]


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceStorageInfo(
    _base.Shape,
    shape_name='InstanceStorageInfo',
):
    total_size_in_gb: DiskSize | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TotalSizeInGB',
        serialization_name='totalSizeInGB',
        shape_name='DiskSize',
    ))

    disks: DiskInfoList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Disks',
        serialization_name='disks',
        value_type=_base.ListValueType(DiskInfo),
        shape_name='DiskInfoList',
    ))

    nvme_support: EphemeralNvmeSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NvmeSupport',
        serialization_name='nvmeSupport',
        shape_name='EphemeralNvmeSupport',
    ))

    encryption_support: InstanceStorageEncryptionSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EncryptionSupport',
        serialization_name='encryptionSupport',
        shape_name='InstanceStorageEncryptionSupport',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InternetGateway(
    _base.Shape,
    shape_name='InternetGateway',
):
    attachments: InternetGatewayAttachmentList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Attachments',
        serialization_name='attachmentSet',
        value_type=_base.ListValueType(InternetGatewayAttachment),
        shape_name='InternetGatewayAttachmentList',
    ))

    internet_gateway_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InternetGatewayId',
        serialization_name='internetGatewayId',
        shape_name='String',
    ))

    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='ownerId',
        shape_name='String',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class IpPermission(
    _base.Shape,
    shape_name='IpPermission',
):
    ip_protocol: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IpProtocol',
        serialization_name='ipProtocol',
        shape_name='String',
    ))

    from_port: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='FromPort',
        serialization_name='fromPort',
        shape_name='Integer',
    ))

    to_port: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ToPort',
        serialization_name='toPort',
        shape_name='Integer',
    ))

    user_id_group_pairs: UserIdGroupPairList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UserIdGroupPairs',
        serialization_name='groups',
        value_type=_base.ListValueType(UserIdGroupPair),
        shape_name='UserIdGroupPairList',
    ))

    ip_ranges: IpRangeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IpRanges',
        serialization_name='ipRanges',
        value_type=_base.ListValueType(IpRange),
        shape_name='IpRangeList',
    ))

    ipv6_ranges: Ipv6RangeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Ranges',
        serialization_name='ipv6Ranges',
        value_type=_base.ListValueType(Ipv6Range),
        shape_name='Ipv6RangeList',
    ))

    prefix_list_ids: PrefixListIdList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrefixListIds',
        serialization_name='prefixListIds',
        value_type=_base.ListValueType(PrefixListId),
        shape_name='PrefixListIdList',
    ))


MediaDeviceInfoList: _ta.TypeAlias = _ta.Sequence[MediaDeviceInfo]


@_dc.dataclass(frozen=True, kw_only=True)
class NetworkInfo(
    _base.Shape,
    shape_name='NetworkInfo',
):
    network_performance: NetworkPerformance | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkPerformance',
        serialization_name='networkPerformance',
        shape_name='NetworkPerformance',
    ))

    maximum_network_interfaces: MaxNetworkInterfaces | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaximumNetworkInterfaces',
        serialization_name='maximumNetworkInterfaces',
        shape_name='MaxNetworkInterfaces',
    ))

    maximum_network_cards: MaximumNetworkCards | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaximumNetworkCards',
        serialization_name='maximumNetworkCards',
        shape_name='MaximumNetworkCards',
    ))

    default_network_card_index: DefaultNetworkCardIndex | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DefaultNetworkCardIndex',
        serialization_name='defaultNetworkCardIndex',
        shape_name='DefaultNetworkCardIndex',
    ))

    network_cards: NetworkCardInfoList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkCards',
        serialization_name='networkCards',
        value_type=_base.ListValueType(NetworkCardInfo),
        shape_name='NetworkCardInfoList',
    ))

    ipv4_addresses_per_interface: MaxIpv4AddrPerInterface | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv4AddressesPerInterface',
        serialization_name='ipv4AddressesPerInterface',
        shape_name='MaxIpv4AddrPerInterface',
    ))

    ipv6_addresses_per_interface: MaxIpv6AddrPerInterface | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6AddressesPerInterface',
        serialization_name='ipv6AddressesPerInterface',
        shape_name='MaxIpv6AddrPerInterface',
    ))

    ipv6_supported: Ipv6Flag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Supported',
        serialization_name='ipv6Supported',
        shape_name='Ipv6Flag',
    ))

    ena_support: EnaSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSupport',
        serialization_name='enaSupport',
        shape_name='EnaSupport',
    ))

    efa_supported: EfaSupportedFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EfaSupported',
        serialization_name='efaSupported',
        shape_name='EfaSupportedFlag',
    ))

    efa_info: EfaInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EfaInfo',
        serialization_name='efaInfo',
        shape_name='EfaInfo',
    ))

    encryption_in_transit_supported: EncryptionInTransitSupported | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EncryptionInTransitSupported',
        serialization_name='encryptionInTransitSupported',
        shape_name='EncryptionInTransitSupported',
    ))

    ena_srd_supported: EnaSrdSupported | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdSupported',
        serialization_name='enaSrdSupported',
        shape_name='EnaSrdSupported',
    ))

    bandwidth_weightings: BandwidthWeightingTypeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BandwidthWeightings',
        serialization_name='bandwidthWeightings',
        value_type=_base.ListValueType(BandwidthWeightingType),
        shape_name='BandwidthWeightingTypeList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NetworkInterfaceAttachment(
    _base.Shape,
    shape_name='NetworkInterfaceAttachment',
):
    attach_time: _base.DateTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AttachTime',
        serialization_name='attachTime',
        shape_name='DateTime',
    ))

    attachment_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AttachmentId',
        serialization_name='attachmentId',
        shape_name='String',
    ))

    delete_on_termination: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        serialization_name='deleteOnTermination',
        shape_name='Boolean',
    ))

    device_index: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeviceIndex',
        serialization_name='deviceIndex',
        shape_name='Integer',
    ))

    network_card_index: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkCardIndex',
        serialization_name='networkCardIndex',
        shape_name='Integer',
    ))

    instance_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceId',
        serialization_name='instanceId',
        shape_name='String',
    ))

    instance_owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceOwnerId',
        serialization_name='instanceOwnerId',
        shape_name='String',
    ))

    status: AttachmentStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Status',
        serialization_name='status',
        shape_name='AttachmentStatus',
    ))

    ena_srd_specification: AttachmentEnaSrdSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSrdSpecification',
        serialization_name='enaSrdSpecification',
        shape_name='AttachmentEnaSrdSpecification',
    ))


NetworkInterfacePrivateIpAddressList: _ta.TypeAlias = _ta.Sequence[NetworkInterfacePrivateIpAddress]

NeuronDeviceInfoList: _ta.TypeAlias = _ta.Sequence[NeuronDeviceInfo]

RouteTableAssociationList: _ta.TypeAlias = _ta.Sequence[RouteTableAssociation]

SubnetIpv6CidrBlockAssociationSet: _ta.TypeAlias = _ta.Sequence[SubnetIpv6CidrBlockAssociation]

VpcCidrBlockAssociationSet: _ta.TypeAlias = _ta.Sequence[VpcCidrBlockAssociation]


@_dc.dataclass(frozen=True, kw_only=True)
class VpcEncryptionControl(
    _base.Shape,
    shape_name='VpcEncryptionControl',
):
    vpc_id: VpcId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='VpcId',
    ))

    vpc_encryption_control_id: VpcEncryptionControlId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcEncryptionControlId',
        serialization_name='vpcEncryptionControlId',
        shape_name='VpcEncryptionControlId',
    ))

    mode: VpcEncryptionControlMode | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Mode',
        serialization_name='mode',
        shape_name='VpcEncryptionControlMode',
    ))

    state: VpcEncryptionControlState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='VpcEncryptionControlState',
    ))

    state_message: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StateMessage',
        serialization_name='stateMessage',
        shape_name='String',
    ))

    resource_exclusions: VpcEncryptionControlExclusions | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ResourceExclusions',
        serialization_name='resourceExclusions',
        shape_name='VpcEncryptionControlExclusions',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))


VpcIpv6CidrBlockAssociationSet: _ta.TypeAlias = _ta.Sequence[VpcIpv6CidrBlockAssociation]


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeAddressesRequest(
    _base.Shape,
    shape_name='DescribeAddressesRequest',
):
    public_ips: PublicIpStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicIps',
        serialization_name='PublicIp',
        value_type=_base.ListValueType(str),
        shape_name='PublicIpStringList',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))

    allocation_ids: AllocationIdList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AllocationIds',
        serialization_name='AllocationId',
        value_type=_base.ListValueType(AllocationId),
        shape_name='AllocationIdList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeImagesRequest(
    _base.Shape,
    shape_name='DescribeImagesRequest',
):
    executable_users: ExecutableByStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ExecutableUsers',
        serialization_name='ExecutableBy',
        value_type=_base.ListValueType(str),
        shape_name='ExecutableByStringList',
    ))

    image_ids: ImageIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImageIds',
        serialization_name='ImageId',
        value_type=_base.ListValueType(ImageId),
        shape_name='ImageIdStringList',
    ))

    owners: OwnerStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Owners',
        serialization_name='Owner',
        value_type=_base.ListValueType(str),
        shape_name='OwnerStringList',
    ))

    include_deprecated: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IncludeDeprecated',
        shape_name='Boolean',
    ))

    include_disabled: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IncludeDisabled',
        shape_name='Boolean',
    ))

    max_results: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='Integer',
    ))

    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeInstanceTypesRequest(
    _base.Shape,
    shape_name='DescribeInstanceTypesRequest',
):
    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    instance_types: RequestInstanceTypeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceTypes',
        serialization_name='InstanceType',
        value_type=_base.ListValueType(InstanceType),
        shape_name='RequestInstanceTypeList',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))

    max_results: DITMaxResults | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DITMaxResults',
    ))

    next_token: NextToken | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='NextToken',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeInstancesRequest(
    _base.Shape,
    shape_name='DescribeInstancesRequest',
):
    instance_ids: InstanceIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceIds',
        serialization_name='InstanceId',
        value_type=_base.ListValueType(InstanceId),
        shape_name='InstanceIdStringList',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))

    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))

    max_results: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        serialization_name='maxResults',
        shape_name='Integer',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeInternetGatewaysRequest(
    _base.Shape,
    shape_name='DescribeInternetGatewaysRequest',
):
    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeInternetGatewaysMaxResults | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeInternetGatewaysMaxResults',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    internet_gateway_ids: InternetGatewayIdList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InternetGatewayIds',
        serialization_name='internetGatewayId',
        value_type=_base.ListValueType(InternetGatewayId),
        shape_name='InternetGatewayIdList',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeKeyPairsRequest(
    _base.Shape,
    shape_name='DescribeKeyPairsRequest',
):
    key_names: KeyNameStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyNames',
        serialization_name='KeyName',
        value_type=_base.ListValueType(KeyPairName),
        shape_name='KeyNameStringList',
    ))

    key_pair_ids: KeyPairIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyPairIds',
        serialization_name='KeyPairId',
        value_type=_base.ListValueType(KeyPairId),
        shape_name='KeyPairIdStringList',
    ))

    include_public_key: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IncludePublicKey',
        shape_name='Boolean',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeNetworkInterfacesRequest(
    _base.Shape,
    shape_name='DescribeNetworkInterfacesRequest',
):
    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeNetworkInterfacesMaxResults | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeNetworkInterfacesMaxResults',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    network_interface_ids: NetworkInterfaceIdList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaceIds',
        serialization_name='NetworkInterfaceId',
        value_type=_base.ListValueType(NetworkInterfaceId),
        shape_name='NetworkInterfaceIdList',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeRouteTablesRequest(
    _base.Shape,
    shape_name='DescribeRouteTablesRequest',
):
    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeRouteTablesMaxResults | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeRouteTablesMaxResults',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    route_table_ids: RouteTableIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RouteTableIds',
        serialization_name='RouteTableId',
        value_type=_base.ListValueType(RouteTableId),
        shape_name='RouteTableIdStringList',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeSecurityGroupsRequest(
    _base.Shape,
    shape_name='DescribeSecurityGroupsRequest',
):
    group_ids: GroupIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupIds',
        serialization_name='GroupId',
        value_type=_base.ListValueType(SecurityGroupId),
        shape_name='GroupIdStringList',
    ))

    group_names: GroupNameStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupNames',
        serialization_name='GroupName',
        value_type=_base.ListValueType(SecurityGroupName),
        shape_name='GroupNameStringList',
    ))

    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeSecurityGroupsMaxResults | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeSecurityGroupsMaxResults',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeSubnetsRequest(
    _base.Shape,
    shape_name='DescribeSubnetsRequest',
):
    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))

    subnet_ids: SubnetIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetIds',
        serialization_name='SubnetId',
        value_type=_base.ListValueType(SubnetId),
        shape_name='SubnetIdStringList',
    ))

    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeSubnetsMaxResults | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeSubnetsMaxResults',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeVpcsRequest(
    _base.Shape,
    shape_name='DescribeVpcsRequest',
):
    filters: FilterList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Filters',
        serialization_name='Filter',
        value_type=_base.ListValueType(Filter),
        shape_name='FilterList',
    ))

    vpc_ids: VpcIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcIds',
        serialization_name='VpcId',
        value_type=_base.ListValueType(VpcId),
        shape_name='VpcIdStringList',
    ))

    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeVpcsMaxResults | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeVpcsMaxResults',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class FpgaInfo(
    _base.Shape,
    shape_name='FpgaInfo',
):
    fpgas: FpgaDeviceInfoList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Fpgas',
        serialization_name='fpgas',
        value_type=_base.ListValueType(FpgaDeviceInfo),
        shape_name='FpgaDeviceInfoList',
    ))

    total_fpga_memory_in_mi_b: TotalFpgaMemory | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TotalFpgaMemoryInMiB',
        serialization_name='totalFpgaMemoryInMiB',
        shape_name='totalFpgaMemory',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class GpuInfo(
    _base.Shape,
    shape_name='GpuInfo',
):
    gpus: GpuDeviceInfoList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Gpus',
        serialization_name='gpus',
        value_type=_base.ListValueType(GpuDeviceInfo),
        shape_name='GpuDeviceInfoList',
    ))

    total_gpu_memory_in_mi_b: TotalGpuMemory | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TotalGpuMemoryInMiB',
        serialization_name='totalGpuMemoryInMiB',
        shape_name='totalGpuMemory',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Image(
    _base.Shape,
    shape_name='Image',
):
    platform_details: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PlatformDetails',
        serialization_name='platformDetails',
        shape_name='String',
    ))

    usage_operation: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UsageOperation',
        serialization_name='usageOperation',
        shape_name='String',
    ))

    block_device_mappings: BlockDeviceMappingList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BlockDeviceMappings',
        serialization_name='blockDeviceMapping',
        value_type=_base.ListValueType(BlockDeviceMapping),
        shape_name='BlockDeviceMappingList',
    ))

    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='description',
        shape_name='String',
    ))

    ena_support: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSupport',
        serialization_name='enaSupport',
        shape_name='Boolean',
    ))

    hypervisor: HypervisorType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Hypervisor',
        serialization_name='hypervisor',
        shape_name='HypervisorType',
    ))

    image_owner_alias: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImageOwnerAlias',
        serialization_name='imageOwnerAlias',
        shape_name='String',
    ))

    name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Name',
        serialization_name='name',
        shape_name='String',
    ))

    root_device_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RootDeviceName',
        serialization_name='rootDeviceName',
        shape_name='String',
    ))

    root_device_type: DeviceType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RootDeviceType',
        serialization_name='rootDeviceType',
        shape_name='DeviceType',
    ))

    sriov_net_support: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SriovNetSupport',
        serialization_name='sriovNetSupport',
        shape_name='String',
    ))

    state_reason: StateReason | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StateReason',
        serialization_name='stateReason',
        shape_name='StateReason',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    virtualization_type: VirtualizationType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VirtualizationType',
        serialization_name='virtualizationType',
        shape_name='VirtualizationType',
    ))

    boot_mode: BootModeValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BootMode',
        serialization_name='bootMode',
        shape_name='BootModeValues',
    ))

    tpm_support: TpmSupportValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TpmSupport',
        serialization_name='tpmSupport',
        shape_name='TpmSupportValues',
    ))

    deprecation_time: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeprecationTime',
        serialization_name='deprecationTime',
        shape_name='String',
    ))

    imds_support: ImdsSupportValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImdsSupport',
        serialization_name='imdsSupport',
        shape_name='ImdsSupportValues',
    ))

    source_instance_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SourceInstanceId',
        serialization_name='sourceInstanceId',
        shape_name='String',
    ))

    deregistration_protection: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DeregistrationProtection',
        serialization_name='deregistrationProtection',
        shape_name='String',
    ))

    last_launched_time: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LastLaunchedTime',
        serialization_name='lastLaunchedTime',
        shape_name='String',
    ))

    image_allowed: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImageAllowed',
        serialization_name='imageAllowed',
        shape_name='Boolean',
    ))

    source_image_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SourceImageId',
        serialization_name='sourceImageId',
        shape_name='String',
    ))

    source_image_region: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SourceImageRegion',
        serialization_name='sourceImageRegion',
        shape_name='String',
    ))

    image_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImageId',
        serialization_name='imageId',
        shape_name='String',
    ))

    image_location: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImageLocation',
        serialization_name='imageLocation',
        shape_name='String',
    ))

    state: ImageState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='imageState',
        shape_name='ImageState',
    ))

    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='imageOwnerId',
        shape_name='String',
    ))

    creation_date: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CreationDate',
        serialization_name='creationDate',
        shape_name='String',
    ))

    public: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Public',
        serialization_name='isPublic',
        shape_name='Boolean',
    ))

    product_codes: ProductCodeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ProductCodes',
        serialization_name='productCodes',
        value_type=_base.ListValueType(ProductCode),
        shape_name='ProductCodeList',
    ))

    architecture: ArchitectureValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Architecture',
        serialization_name='architecture',
        shape_name='ArchitectureValues',
    ))

    image_type: ImageTypeValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImageType',
        serialization_name='imageType',
        shape_name='ImageTypeValues',
    ))

    kernel_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KernelId',
        serialization_name='kernelId',
        shape_name='String',
    ))

    ramdisk_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RamdiskId',
        serialization_name='ramdiskId',
        shape_name='String',
    ))

    platform: PlatformValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Platform',
        serialization_name='platform',
        shape_name='PlatformValues',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class InferenceAcceleratorInfo(
    _base.Shape,
    shape_name='InferenceAcceleratorInfo',
):
    accelerators: InferenceDeviceInfoList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Accelerators',
        serialization_name='accelerators',
        value_type=_base.ListValueType(InferenceDeviceInfo),
        shape_name='InferenceDeviceInfoList',
    ))

    total_inference_memory_in_mi_b: TotalInferenceMemory | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TotalInferenceMemoryInMiB',
        serialization_name='totalInferenceMemoryInMiB',
        shape_name='totalInferenceMemory',
    ))


InstanceBlockDeviceMappingList: _ta.TypeAlias = _ta.Sequence[InstanceBlockDeviceMapping]


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceNetworkInterface(
    _base.Shape,
    shape_name='InstanceNetworkInterface',
):
    association: InstanceNetworkInterfaceAssociation | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Association',
        serialization_name='association',
        shape_name='InstanceNetworkInterfaceAssociation',
    ))

    attachment: InstanceNetworkInterfaceAttachment | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Attachment',
        serialization_name='attachment',
        shape_name='InstanceNetworkInterfaceAttachment',
    ))

    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='description',
        shape_name='String',
    ))

    groups: GroupIdentifierList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Groups',
        serialization_name='groupSet',
        value_type=_base.ListValueType(GroupIdentifier),
        shape_name='GroupIdentifierList',
    ))

    ipv6_addresses: InstanceIpv6AddressList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Addresses',
        serialization_name='ipv6AddressesSet',
        value_type=_base.ListValueType(InstanceIpv6Address),
        shape_name='InstanceIpv6AddressList',
    ))

    mac_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MacAddress',
        serialization_name='macAddress',
        shape_name='String',
    ))

    network_interface_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        serialization_name='networkInterfaceId',
        shape_name='String',
    ))

    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='ownerId',
        shape_name='String',
    ))

    private_dns_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        serialization_name='privateDnsName',
        shape_name='String',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))

    private_ip_addresses: InstancePrivateIpAddressList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddresses',
        serialization_name='privateIpAddressesSet',
        value_type=_base.ListValueType(InstancePrivateIpAddress),
        shape_name='InstancePrivateIpAddressList',
    ))

    source_dest_check: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SourceDestCheck',
        serialization_name='sourceDestCheck',
        shape_name='Boolean',
    ))

    status: NetworkInterfaceStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Status',
        serialization_name='status',
        shape_name='NetworkInterfaceStatus',
    ))

    subnet_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetId',
        serialization_name='subnetId',
        shape_name='String',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))

    interface_type: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InterfaceType',
        serialization_name='interfaceType',
        shape_name='String',
    ))

    ipv4_prefixes: InstanceIpv4PrefixList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv4Prefixes',
        serialization_name='ipv4PrefixSet',
        value_type=_base.ListValueType(InstanceIpv4Prefix),
        shape_name='InstanceIpv4PrefixList',
    ))

    ipv6_prefixes: InstanceIpv6PrefixList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Prefixes',
        serialization_name='ipv6PrefixSet',
        value_type=_base.ListValueType(InstanceIpv6Prefix),
        shape_name='InstanceIpv6PrefixList',
    ))

    connection_tracking_configuration: ConnectionTrackingSpecificationResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ConnectionTrackingConfiguration',
        serialization_name='connectionTrackingConfiguration',
        shape_name='ConnectionTrackingSpecificationResponse',
    ))

    operator: OperatorResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Operator',
        serialization_name='operator',
        shape_name='OperatorResponse',
    ))


InstanceNetworkInterfaceSpecificationList: _ta.TypeAlias = _ta.Sequence[InstanceNetworkInterfaceSpecification]

InternetGatewayList: _ta.TypeAlias = _ta.Sequence[InternetGateway]

IpPermissionList: _ta.TypeAlias = _ta.Sequence[IpPermission]


@_dc.dataclass(frozen=True, kw_only=True)
class MediaAcceleratorInfo(
    _base.Shape,
    shape_name='MediaAcceleratorInfo',
):
    accelerators: MediaDeviceInfoList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Accelerators',
        serialization_name='accelerators',
        value_type=_base.ListValueType(MediaDeviceInfo),
        shape_name='MediaDeviceInfoList',
    ))

    total_media_memory_in_mi_b: TotalMediaMemory | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TotalMediaMemoryInMiB',
        serialization_name='totalMediaMemoryInMiB',
        shape_name='TotalMediaMemory',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NetworkInterface(
    _base.Shape,
    shape_name='NetworkInterface',
):
    association: NetworkInterfaceAssociation | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Association',
        serialization_name='association',
        shape_name='NetworkInterfaceAssociation',
    ))

    attachment: NetworkInterfaceAttachment | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Attachment',
        serialization_name='attachment',
        shape_name='NetworkInterfaceAttachment',
    ))

    availability_zone: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AvailabilityZone',
        serialization_name='availabilityZone',
        shape_name='String',
    ))

    connection_tracking_configuration: ConnectionTrackingConfiguration | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ConnectionTrackingConfiguration',
        serialization_name='connectionTrackingConfiguration',
        shape_name='ConnectionTrackingConfiguration',
    ))

    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='description',
        shape_name='String',
    ))

    groups: GroupIdentifierList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Groups',
        serialization_name='groupSet',
        value_type=_base.ListValueType(GroupIdentifier),
        shape_name='GroupIdentifierList',
    ))

    interface_type: NetworkInterfaceType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InterfaceType',
        serialization_name='interfaceType',
        shape_name='NetworkInterfaceType',
    ))

    ipv6_addresses: NetworkInterfaceIpv6AddressesList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Addresses',
        serialization_name='ipv6AddressesSet',
        value_type=_base.ListValueType(NetworkInterfaceIpv6Address),
        shape_name='NetworkInterfaceIpv6AddressesList',
    ))

    mac_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MacAddress',
        serialization_name='macAddress',
        shape_name='String',
    ))

    network_interface_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        serialization_name='networkInterfaceId',
        shape_name='String',
    ))

    outpost_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OutpostArn',
        serialization_name='outpostArn',
        shape_name='String',
    ))

    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='ownerId',
        shape_name='String',
    ))

    private_dns_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        serialization_name='privateDnsName',
        shape_name='String',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))

    private_ip_addresses: NetworkInterfacePrivateIpAddressList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddresses',
        serialization_name='privateIpAddressesSet',
        value_type=_base.ListValueType(NetworkInterfacePrivateIpAddress),
        shape_name='NetworkInterfacePrivateIpAddressList',
    ))

    ipv4_prefixes: Ipv4PrefixesList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv4Prefixes',
        serialization_name='ipv4PrefixSet',
        value_type=_base.ListValueType(Ipv4PrefixSpecification),
        shape_name='Ipv4PrefixesList',
    ))

    ipv6_prefixes: Ipv6PrefixesList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Prefixes',
        serialization_name='ipv6PrefixSet',
        value_type=_base.ListValueType(Ipv6PrefixSpecification),
        shape_name='Ipv6PrefixesList',
    ))

    requester_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequesterId',
        serialization_name='requesterId',
        shape_name='String',
    ))

    requester_managed: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequesterManaged',
        serialization_name='requesterManaged',
        shape_name='Boolean',
    ))

    source_dest_check: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SourceDestCheck',
        serialization_name='sourceDestCheck',
        shape_name='Boolean',
    ))

    status: NetworkInterfaceStatus | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Status',
        serialization_name='status',
        shape_name='NetworkInterfaceStatus',
    ))

    subnet_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetId',
        serialization_name='subnetId',
        shape_name='String',
    ))

    tag_set: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TagSet',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))

    deny_all_igw_traffic: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DenyAllIgwTraffic',
        serialization_name='denyAllIgwTraffic',
        shape_name='Boolean',
    ))

    ipv6_native: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Native',
        serialization_name='ipv6Native',
        shape_name='Boolean',
    ))

    ipv6_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Address',
        serialization_name='ipv6Address',
        shape_name='String',
    ))

    operator: OperatorResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Operator',
        serialization_name='operator',
        shape_name='OperatorResponse',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class NeuronInfo(
    _base.Shape,
    shape_name='NeuronInfo',
):
    neuron_devices: NeuronDeviceInfoList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NeuronDevices',
        serialization_name='neuronDevices',
        value_type=_base.ListValueType(NeuronDeviceInfo),
        shape_name='NeuronDeviceInfoList',
    ))

    total_neuron_device_memory_in_mi_b: TotalNeuronMemory | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TotalNeuronDeviceMemoryInMiB',
        serialization_name='totalNeuronDeviceMemoryInMiB',
        shape_name='TotalNeuronMemory',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class RouteTable(
    _base.Shape,
    shape_name='RouteTable',
):
    associations: RouteTableAssociationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Associations',
        serialization_name='associationSet',
        value_type=_base.ListValueType(RouteTableAssociation),
        shape_name='RouteTableAssociationList',
    ))

    propagating_vgws: PropagatingVgwList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PropagatingVgws',
        serialization_name='propagatingVgwSet',
        value_type=_base.ListValueType(PropagatingVgw),
        shape_name='PropagatingVgwList',
    ))

    route_table_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RouteTableId',
        serialization_name='routeTableId',
        shape_name='String',
    ))

    routes: RouteList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Routes',
        serialization_name='routeSet',
        value_type=_base.ListValueType(Route),
        shape_name='RouteList',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))

    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='ownerId',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class StartInstancesResult(
    _base.Shape,
    shape_name='StartInstancesResult',
):
    starting_instances: InstanceStateChangeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StartingInstances',
        serialization_name='instancesSet',
        value_type=_base.ListValueType(InstanceStateChange),
        shape_name='InstanceStateChangeList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class StopInstancesResult(
    _base.Shape,
    shape_name='StopInstancesResult',
):
    stopping_instances: InstanceStateChangeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StoppingInstances',
        serialization_name='instancesSet',
        value_type=_base.ListValueType(InstanceStateChange),
        shape_name='InstanceStateChangeList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Subnet(
    _base.Shape,
    shape_name='Subnet',
):
    availability_zone_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AvailabilityZoneId',
        serialization_name='availabilityZoneId',
        shape_name='String',
    ))

    enable_lni_at_device_index: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnableLniAtDeviceIndex',
        serialization_name='enableLniAtDeviceIndex',
        shape_name='Integer',
    ))

    map_customer_owned_ip_on_launch: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MapCustomerOwnedIpOnLaunch',
        serialization_name='mapCustomerOwnedIpOnLaunch',
        shape_name='Boolean',
    ))

    customer_owned_ipv4_pool: CoipPoolId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CustomerOwnedIpv4Pool',
        serialization_name='customerOwnedIpv4Pool',
        shape_name='CoipPoolId',
    ))

    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='ownerId',
        shape_name='String',
    ))

    assign_ipv6_address_on_creation: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AssignIpv6AddressOnCreation',
        serialization_name='assignIpv6AddressOnCreation',
        shape_name='Boolean',
    ))

    ipv6_cidr_block_association_set: SubnetIpv6CidrBlockAssociationSet | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6CidrBlockAssociationSet',
        serialization_name='ipv6CidrBlockAssociationSet',
        value_type=_base.ListValueType(SubnetIpv6CidrBlockAssociation),
        shape_name='SubnetIpv6CidrBlockAssociationSet',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    subnet_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetArn',
        serialization_name='subnetArn',
        shape_name='String',
    ))

    outpost_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OutpostArn',
        serialization_name='outpostArn',
        shape_name='String',
    ))

    enable_dns64: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnableDns64',
        serialization_name='enableDns64',
        shape_name='Boolean',
    ))

    ipv6_native: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Native',
        serialization_name='ipv6Native',
        shape_name='Boolean',
    ))

    private_dns_name_options_on_launch: PrivateDnsNameOptionsOnLaunch | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateDnsNameOptionsOnLaunch',
        serialization_name='privateDnsNameOptionsOnLaunch',
        shape_name='PrivateDnsNameOptionsOnLaunch',
    ))

    block_public_access_states: BlockPublicAccessStates | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BlockPublicAccessStates',
        serialization_name='blockPublicAccessStates',
        shape_name='BlockPublicAccessStates',
    ))

    subnet_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetId',
        serialization_name='subnetId',
        shape_name='String',
    ))

    state: SubnetState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='SubnetState',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))

    cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CidrBlock',
        serialization_name='cidrBlock',
        shape_name='String',
    ))

    available_ip_address_count: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AvailableIpAddressCount',
        serialization_name='availableIpAddressCount',
        shape_name='Integer',
    ))

    availability_zone: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AvailabilityZone',
        serialization_name='availabilityZone',
        shape_name='String',
    ))

    default_for_az: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DefaultForAz',
        serialization_name='defaultForAz',
        shape_name='Boolean',
    ))

    map_public_ip_on_launch: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MapPublicIpOnLaunch',
        serialization_name='mapPublicIpOnLaunch',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class TerminateInstancesResult(
    _base.Shape,
    shape_name='TerminateInstancesResult',
):
    terminating_instances: InstanceStateChangeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TerminatingInstances',
        serialization_name='instancesSet',
        value_type=_base.ListValueType(InstanceStateChange),
        shape_name='InstanceStateChangeList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Vpc(
    _base.Shape,
    shape_name='Vpc',
):
    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='ownerId',
        shape_name='String',
    ))

    instance_tenancy: Tenancy | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceTenancy',
        serialization_name='instanceTenancy',
        shape_name='Tenancy',
    ))

    ipv6_cidr_block_association_set: VpcIpv6CidrBlockAssociationSet | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6CidrBlockAssociationSet',
        serialization_name='ipv6CidrBlockAssociationSet',
        value_type=_base.ListValueType(VpcIpv6CidrBlockAssociation),
        shape_name='VpcIpv6CidrBlockAssociationSet',
    ))

    cidr_block_association_set: VpcCidrBlockAssociationSet | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CidrBlockAssociationSet',
        serialization_name='cidrBlockAssociationSet',
        value_type=_base.ListValueType(VpcCidrBlockAssociation),
        shape_name='VpcCidrBlockAssociationSet',
    ))

    is_default: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IsDefault',
        serialization_name='isDefault',
        shape_name='Boolean',
    ))

    encryption_control: VpcEncryptionControl | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EncryptionControl',
        serialization_name='encryptionControl',
        shape_name='VpcEncryptionControl',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    block_public_access_states: BlockPublicAccessStates | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BlockPublicAccessStates',
        serialization_name='blockPublicAccessStates',
        shape_name='BlockPublicAccessStates',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))

    state: VpcState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='state',
        shape_name='VpcState',
    ))

    cidr_block: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CidrBlock',
        serialization_name='cidrBlock',
        shape_name='String',
    ))

    dhcp_options_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DhcpOptionsId',
        serialization_name='dhcpOptionsId',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class CreateRouteTableResult(
    _base.Shape,
    shape_name='CreateRouteTableResult',
):
    route_table: RouteTable | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RouteTable',
        serialization_name='routeTable',
        shape_name='RouteTable',
    ))

    client_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ClientToken',
        serialization_name='clientToken',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeInternetGatewaysResult(
    _base.Shape,
    shape_name='DescribeInternetGatewaysResult',
):
    internet_gateways: InternetGatewayList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InternetGateways',
        serialization_name='internetGatewaySet',
        value_type=_base.ListValueType(InternetGateway),
        shape_name='InternetGatewayList',
    ))

    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))


ImageList: _ta.TypeAlias = _ta.Sequence[Image]

InstanceNetworkInterfaceList: _ta.TypeAlias = _ta.Sequence[InstanceNetworkInterface]


@_dc.dataclass(frozen=True, kw_only=True)
class InstanceTypeInfo(
    _base.Shape,
    shape_name='InstanceTypeInfo',
):
    instance_type: InstanceType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceType',
        serialization_name='instanceType',
        shape_name='InstanceType',
    ))

    current_generation: CurrentGenerationFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CurrentGeneration',
        serialization_name='currentGeneration',
        shape_name='CurrentGenerationFlag',
    ))

    free_tier_eligible: FreeTierEligibleFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='FreeTierEligible',
        serialization_name='freeTierEligible',
        shape_name='FreeTierEligibleFlag',
    ))

    supported_usage_classes: UsageClassTypeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SupportedUsageClasses',
        serialization_name='supportedUsageClasses',
        value_type=_base.ListValueType(UsageClassType),
        shape_name='UsageClassTypeList',
    ))

    supported_root_device_types: RootDeviceTypeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SupportedRootDeviceTypes',
        serialization_name='supportedRootDeviceTypes',
        value_type=_base.ListValueType(RootDeviceType),
        shape_name='RootDeviceTypeList',
    ))

    supported_virtualization_types: VirtualizationTypeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SupportedVirtualizationTypes',
        serialization_name='supportedVirtualizationTypes',
        value_type=_base.ListValueType(VirtualizationType),
        shape_name='VirtualizationTypeList',
    ))

    bare_metal: BareMetalFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BareMetal',
        serialization_name='bareMetal',
        shape_name='BareMetalFlag',
    ))

    hypervisor: InstanceTypeHypervisor | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Hypervisor',
        serialization_name='hypervisor',
        shape_name='InstanceTypeHypervisor',
    ))

    processor_info: ProcessorInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ProcessorInfo',
        serialization_name='processorInfo',
        shape_name='ProcessorInfo',
    ))

    v_cpu_info: VCpuInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VCpuInfo',
        serialization_name='vCpuInfo',
        shape_name='VCpuInfo',
    ))

    memory_info: MemoryInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MemoryInfo',
        serialization_name='memoryInfo',
        shape_name='MemoryInfo',
    ))

    instance_storage_supported: InstanceStorageFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceStorageSupported',
        serialization_name='instanceStorageSupported',
        shape_name='InstanceStorageFlag',
    ))

    instance_storage_info: InstanceStorageInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceStorageInfo',
        serialization_name='instanceStorageInfo',
        shape_name='InstanceStorageInfo',
    ))

    ebs_info: EbsInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EbsInfo',
        serialization_name='ebsInfo',
        shape_name='EbsInfo',
    ))

    network_info: NetworkInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInfo',
        serialization_name='networkInfo',
        shape_name='NetworkInfo',
    ))

    gpu_info: GpuInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GpuInfo',
        serialization_name='gpuInfo',
        shape_name='GpuInfo',
    ))

    fpga_info: FpgaInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='FpgaInfo',
        serialization_name='fpgaInfo',
        shape_name='FpgaInfo',
    ))

    placement_group_info: PlacementGroupInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PlacementGroupInfo',
        serialization_name='placementGroupInfo',
        shape_name='PlacementGroupInfo',
    ))

    inference_accelerator_info: InferenceAcceleratorInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InferenceAcceleratorInfo',
        serialization_name='inferenceAcceleratorInfo',
        shape_name='InferenceAcceleratorInfo',
    ))

    hibernation_supported: HibernationFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HibernationSupported',
        serialization_name='hibernationSupported',
        shape_name='HibernationFlag',
    ))

    burstable_performance_supported: BurstablePerformanceFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BurstablePerformanceSupported',
        serialization_name='burstablePerformanceSupported',
        shape_name='BurstablePerformanceFlag',
    ))

    dedicated_hosts_supported: DedicatedHostFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DedicatedHostsSupported',
        serialization_name='dedicatedHostsSupported',
        shape_name='DedicatedHostFlag',
    ))

    auto_recovery_supported: AutoRecoveryFlag | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AutoRecoverySupported',
        serialization_name='autoRecoverySupported',
        shape_name='AutoRecoveryFlag',
    ))

    supported_boot_modes: BootModeTypeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SupportedBootModes',
        serialization_name='supportedBootModes',
        value_type=_base.ListValueType(BootModeType),
        shape_name='BootModeTypeList',
    ))

    nitro_enclaves_support: NitroEnclavesSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NitroEnclavesSupport',
        serialization_name='nitroEnclavesSupport',
        shape_name='NitroEnclavesSupport',
    ))

    nitro_tpm_support: NitroTpmSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NitroTpmSupport',
        serialization_name='nitroTpmSupport',
        shape_name='NitroTpmSupport',
    ))

    nitro_tpm_info: NitroTpmInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NitroTpmInfo',
        serialization_name='nitroTpmInfo',
        shape_name='NitroTpmInfo',
    ))

    media_accelerator_info: MediaAcceleratorInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MediaAcceleratorInfo',
        serialization_name='mediaAcceleratorInfo',
        shape_name='MediaAcceleratorInfo',
    ))

    neuron_info: NeuronInfo | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NeuronInfo',
        serialization_name='neuronInfo',
        shape_name='NeuronInfo',
    ))

    phc_support: PhcSupport | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PhcSupport',
        serialization_name='phcSupport',
        shape_name='PhcSupport',
    ))


NetworkInterfaceList: _ta.TypeAlias = _ta.Sequence[NetworkInterface]

RouteTableList: _ta.TypeAlias = _ta.Sequence[RouteTable]


@_dc.dataclass(frozen=True, kw_only=True)
class RunInstancesRequest(
    _base.Shape,
    shape_name='RunInstancesRequest',
):
    block_device_mappings: BlockDeviceMappingRequestList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BlockDeviceMappings',
        serialization_name='BlockDeviceMapping',
        value_type=_base.ListValueType(BlockDeviceMapping),
        shape_name='BlockDeviceMappingRequestList',
    ))

    image_id: ImageId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImageId',
        shape_name='ImageId',
    ))

    instance_type: InstanceType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceType',
        shape_name='InstanceType',
    ))

    ipv6_address_count: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6AddressCount',
        shape_name='Integer',
    ))

    ipv6_addresses: InstanceIpv6AddressList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Addresses',
        serialization_name='Ipv6Address',
        value_type=_base.ListValueType(InstanceIpv6Address),
        shape_name='InstanceIpv6AddressList',
    ))

    kernel_id: KernelId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KernelId',
        shape_name='KernelId',
    ))

    key_name: KeyPairName | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyName',
        shape_name='KeyPairName',
    ))

    max_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='MaxCount',
        shape_name='Integer',
    ))

    min_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='MinCount',
        shape_name='Integer',
    ))

    monitoring: RunInstancesMonitoringEnabled | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Monitoring',
        shape_name='RunInstancesMonitoringEnabled',
    ))

    placement: Placement | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Placement',
        shape_name='Placement',
    ))

    ramdisk_id: RamdiskId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RamdiskId',
        shape_name='RamdiskId',
    ))

    security_group_ids: SecurityGroupIdStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SecurityGroupIds',
        serialization_name='SecurityGroupId',
        value_type=_base.ListValueType(SecurityGroupId),
        shape_name='SecurityGroupIdStringList',
    ))

    security_groups: SecurityGroupStringList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SecurityGroups',
        serialization_name='SecurityGroup',
        value_type=_base.ListValueType(SecurityGroupName),
        shape_name='SecurityGroupStringList',
    ))

    subnet_id: SubnetId | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetId',
        shape_name='SubnetId',
    ))

    user_data: RunInstancesUserData | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UserData',
        shape_name='RunInstancesUserData',
    ))

    elastic_gpu_specification: ElasticGpuSpecifications | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticGpuSpecification',
        value_type=_base.ListValueType(ElasticGpuSpecification),
        shape_name='ElasticGpuSpecifications',
    ))

    elastic_inference_accelerators: ElasticInferenceAccelerators | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticInferenceAccelerators',
        serialization_name='ElasticInferenceAccelerator',
        value_type=_base.ListValueType(ElasticInferenceAccelerator),
        shape_name='ElasticInferenceAccelerators',
    ))

    tag_specifications: TagSpecificationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TagSpecifications',
        serialization_name='TagSpecification',
        value_type=_base.ListValueType(TagSpecification),
        shape_name='TagSpecificationList',
    ))

    launch_template: LaunchTemplateSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LaunchTemplate',
        shape_name='LaunchTemplateSpecification',
    ))

    instance_market_options: InstanceMarketOptionsRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceMarketOptions',
        shape_name='InstanceMarketOptionsRequest',
    ))

    credit_specification: CreditSpecificationRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CreditSpecification',
        shape_name='CreditSpecificationRequest',
    ))

    cpu_options: CpuOptionsRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CpuOptions',
        shape_name='CpuOptionsRequest',
    ))

    capacity_reservation_specification: CapacityReservationSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationSpecification',
        shape_name='CapacityReservationSpecification',
    ))

    hibernation_options: HibernationOptionsRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HibernationOptions',
        shape_name='HibernationOptionsRequest',
    ))

    license_specifications: LicenseSpecificationListRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LicenseSpecifications',
        serialization_name='LicenseSpecification',
        value_type=_base.ListValueType(LicenseConfigurationRequest),
        shape_name='LicenseSpecificationListRequest',
    ))

    metadata_options: InstanceMetadataOptionsRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MetadataOptions',
        shape_name='InstanceMetadataOptionsRequest',
    ))

    enclave_options: EnclaveOptionsRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnclaveOptions',
        shape_name='EnclaveOptionsRequest',
    ))

    private_dns_name_options: PrivateDnsNameOptionsRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateDnsNameOptions',
        shape_name='PrivateDnsNameOptionsRequest',
    ))

    maintenance_options: InstanceMaintenanceOptionsRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaintenanceOptions',
        shape_name='InstanceMaintenanceOptionsRequest',
    ))

    disable_api_stop: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DisableApiStop',
        shape_name='Boolean',
    ))

    enable_primary_ipv6: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnablePrimaryIpv6',
        shape_name='Boolean',
    ))

    network_performance_options: InstanceNetworkPerformanceOptionsRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkPerformanceOptions',
        shape_name='InstanceNetworkPerformanceOptionsRequest',
    ))

    operator: OperatorRequest | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Operator',
        shape_name='OperatorRequest',
    ))

    dry_run: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DryRun',
        serialization_name='dryRun',
        shape_name='Boolean',
    ))

    disable_api_termination: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='DisableApiTermination',
        serialization_name='disableApiTermination',
        shape_name='Boolean',
    ))

    instance_initiated_shutdown_behavior: ShutdownBehavior | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceInitiatedShutdownBehavior',
        serialization_name='instanceInitiatedShutdownBehavior',
        shape_name='ShutdownBehavior',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))

    client_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ClientToken',
        serialization_name='clientToken',
        shape_name='String',
    ))

    additional_info: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AdditionalInfo',
        serialization_name='additionalInfo',
        shape_name='String',
    ))

    network_interfaces: InstanceNetworkInterfaceSpecificationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaces',
        serialization_name='networkInterface',
        value_type=_base.ListValueType(InstanceNetworkInterfaceSpecification),
        shape_name='InstanceNetworkInterfaceSpecificationList',
    ))

    iam_instance_profile: IamInstanceProfileSpecification | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IamInstanceProfile',
        serialization_name='iamInstanceProfile',
        shape_name='IamInstanceProfileSpecification',
    ))

    ebs_optimized: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EbsOptimized',
        serialization_name='ebsOptimized',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class SecurityGroup(
    _base.Shape,
    shape_name='SecurityGroup',
):
    group_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupId',
        serialization_name='groupId',
        shape_name='String',
    ))

    ip_permissions_egress: IpPermissionList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IpPermissionsEgress',
        serialization_name='ipPermissionsEgress',
        value_type=_base.ListValueType(IpPermission),
        shape_name='IpPermissionList',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))

    security_group_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SecurityGroupArn',
        serialization_name='securityGroupArn',
        shape_name='String',
    ))

    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='ownerId',
        shape_name='String',
    ))

    group_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='GroupName',
        serialization_name='groupName',
        shape_name='String',
    ))

    description: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Description',
        serialization_name='groupDescription',
        shape_name='String',
    ))

    ip_permissions: IpPermissionList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IpPermissions',
        serialization_name='ipPermissions',
        value_type=_base.ListValueType(IpPermission),
        shape_name='IpPermissionList',
    ))


SubnetList: _ta.TypeAlias = _ta.Sequence[Subnet]

VpcList: _ta.TypeAlias = _ta.Sequence[Vpc]


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeImagesResult(
    _base.Shape,
    shape_name='DescribeImagesResult',
):
    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))

    images: ImageList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Images',
        serialization_name='imagesSet',
        value_type=_base.ListValueType(Image),
        shape_name='ImageList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeNetworkInterfacesResult(
    _base.Shape,
    shape_name='DescribeNetworkInterfacesResult',
):
    network_interfaces: NetworkInterfaceList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaces',
        serialization_name='networkInterfaceSet',
        value_type=_base.ListValueType(NetworkInterface),
        shape_name='NetworkInterfaceList',
    ))

    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeRouteTablesResult(
    _base.Shape,
    shape_name='DescribeRouteTablesResult',
):
    route_tables: RouteTableList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RouteTables',
        serialization_name='routeTableSet',
        value_type=_base.ListValueType(RouteTable),
        shape_name='RouteTableList',
    ))

    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeSubnetsResult(
    _base.Shape,
    shape_name='DescribeSubnetsResult',
):
    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))

    subnets: SubnetList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Subnets',
        serialization_name='subnetSet',
        value_type=_base.ListValueType(Subnet),
        shape_name='SubnetList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeVpcsResult(
    _base.Shape,
    shape_name='DescribeVpcsResult',
):
    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))

    vpcs: VpcList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Vpcs',
        serialization_name='vpcSet',
        value_type=_base.ListValueType(Vpc),
        shape_name='VpcList',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class Instance(
    _base.Shape,
    shape_name='Instance',
):
    architecture: ArchitectureValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Architecture',
        serialization_name='architecture',
        shape_name='ArchitectureValues',
    ))

    block_device_mappings: InstanceBlockDeviceMappingList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BlockDeviceMappings',
        serialization_name='blockDeviceMapping',
        value_type=_base.ListValueType(InstanceBlockDeviceMapping),
        shape_name='InstanceBlockDeviceMappingList',
    ))

    client_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ClientToken',
        serialization_name='clientToken',
        shape_name='String',
    ))

    ebs_optimized: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EbsOptimized',
        serialization_name='ebsOptimized',
        shape_name='Boolean',
    ))

    ena_support: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnaSupport',
        serialization_name='enaSupport',
        shape_name='Boolean',
    ))

    hypervisor: HypervisorType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Hypervisor',
        serialization_name='hypervisor',
        shape_name='HypervisorType',
    ))

    iam_instance_profile: IamInstanceProfile | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='IamInstanceProfile',
        serialization_name='iamInstanceProfile',
        shape_name='IamInstanceProfile',
    ))

    instance_lifecycle: InstanceLifecycleType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceLifecycle',
        serialization_name='instanceLifecycle',
        shape_name='InstanceLifecycleType',
    ))

    elastic_gpu_associations: ElasticGpuAssociationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticGpuAssociations',
        serialization_name='elasticGpuAssociationSet',
        value_type=_base.ListValueType(ElasticGpuAssociation),
        shape_name='ElasticGpuAssociationList',
    ))

    elastic_inference_accelerator_associations: ElasticInferenceAcceleratorAssociationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorAssociations',
        serialization_name='elasticInferenceAcceleratorAssociationSet',
        value_type=_base.ListValueType(ElasticInferenceAcceleratorAssociation),
        shape_name='ElasticInferenceAcceleratorAssociationList',
    ))

    network_interfaces: InstanceNetworkInterfaceList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkInterfaces',
        serialization_name='networkInterfaceSet',
        value_type=_base.ListValueType(InstanceNetworkInterface),
        shape_name='InstanceNetworkInterfaceList',
    ))

    outpost_arn: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OutpostArn',
        serialization_name='outpostArn',
        shape_name='String',
    ))

    root_device_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RootDeviceName',
        serialization_name='rootDeviceName',
        shape_name='String',
    ))

    root_device_type: DeviceType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RootDeviceType',
        serialization_name='rootDeviceType',
        shape_name='DeviceType',
    ))

    security_groups: GroupIdentifierList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SecurityGroups',
        serialization_name='groupSet',
        value_type=_base.ListValueType(GroupIdentifier),
        shape_name='GroupIdentifierList',
    ))

    source_dest_check: bool | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SourceDestCheck',
        serialization_name='sourceDestCheck',
        shape_name='Boolean',
    ))

    spot_instance_request_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SpotInstanceRequestId',
        serialization_name='spotInstanceRequestId',
        shape_name='String',
    ))

    sriov_net_support: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SriovNetSupport',
        serialization_name='sriovNetSupport',
        shape_name='String',
    ))

    state_reason: StateReason | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StateReason',
        serialization_name='stateReason',
        shape_name='StateReason',
    ))

    tags: _base.TagList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Tags',
        serialization_name='tagSet',
        value_type=_base.ListValueType(_base.Tag),
        shape_name='TagList',
    ))

    virtualization_type: VirtualizationType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VirtualizationType',
        serialization_name='virtualizationType',
        shape_name='VirtualizationType',
    ))

    cpu_options: CpuOptions | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CpuOptions',
        serialization_name='cpuOptions',
        shape_name='CpuOptions',
    ))

    capacity_reservation_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationId',
        serialization_name='capacityReservationId',
        shape_name='String',
    ))

    capacity_reservation_specification: CapacityReservationSpecificationResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CapacityReservationSpecification',
        serialization_name='capacityReservationSpecification',
        shape_name='CapacityReservationSpecificationResponse',
    ))

    hibernation_options: HibernationOptions | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='HibernationOptions',
        serialization_name='hibernationOptions',
        shape_name='HibernationOptions',
    ))

    licenses: LicenseList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Licenses',
        serialization_name='licenseSet',
        value_type=_base.ListValueType(LicenseConfiguration),
        shape_name='LicenseList',
    ))

    metadata_options: InstanceMetadataOptionsResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MetadataOptions',
        serialization_name='metadataOptions',
        shape_name='InstanceMetadataOptionsResponse',
    ))

    enclave_options: EnclaveOptions | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='EnclaveOptions',
        serialization_name='enclaveOptions',
        shape_name='EnclaveOptions',
    ))

    boot_mode: BootModeValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='BootMode',
        serialization_name='bootMode',
        shape_name='BootModeValues',
    ))

    platform_details: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PlatformDetails',
        serialization_name='platformDetails',
        shape_name='String',
    ))

    usage_operation: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UsageOperation',
        serialization_name='usageOperation',
        shape_name='String',
    ))

    usage_operation_update_time: _base.MillisecondDateTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='UsageOperationUpdateTime',
        serialization_name='usageOperationUpdateTime',
        shape_name='MillisecondDateTime',
    ))

    private_dns_name_options: PrivateDnsNameOptionsResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateDnsNameOptions',
        serialization_name='privateDnsNameOptions',
        shape_name='PrivateDnsNameOptionsResponse',
    ))

    ipv6_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Ipv6Address',
        serialization_name='ipv6Address',
        shape_name='String',
    ))

    tpm_support: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='TpmSupport',
        serialization_name='tpmSupport',
        shape_name='String',
    ))

    maintenance_options: InstanceMaintenanceOptions | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='MaintenanceOptions',
        serialization_name='maintenanceOptions',
        shape_name='InstanceMaintenanceOptions',
    ))

    current_instance_boot_mode: InstanceBootModeValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='CurrentInstanceBootMode',
        serialization_name='currentInstanceBootMode',
        shape_name='InstanceBootModeValues',
    ))

    network_performance_options: InstanceNetworkPerformanceOptions | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NetworkPerformanceOptions',
        serialization_name='networkPerformanceOptions',
        shape_name='InstanceNetworkPerformanceOptions',
    ))

    operator: OperatorResponse | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Operator',
        serialization_name='operator',
        shape_name='OperatorResponse',
    ))

    instance_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceId',
        serialization_name='instanceId',
        shape_name='String',
    ))

    image_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ImageId',
        serialization_name='imageId',
        shape_name='String',
    ))

    state: InstanceState | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='State',
        serialization_name='instanceState',
        shape_name='InstanceState',
    ))

    private_dns_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        serialization_name='privateDnsName',
        shape_name='String',
    ))

    public_dns_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicDnsName',
        serialization_name='dnsName',
        shape_name='String',
    ))

    state_transition_reason: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='StateTransitionReason',
        serialization_name='reason',
        shape_name='String',
    ))

    key_name: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KeyName',
        serialization_name='keyName',
        shape_name='String',
    ))

    ami_launch_index: int | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='AmiLaunchIndex',
        serialization_name='amiLaunchIndex',
        shape_name='Integer',
    ))

    product_codes: ProductCodeList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ProductCodes',
        serialization_name='productCodes',
        value_type=_base.ListValueType(ProductCode),
        shape_name='ProductCodeList',
    ))

    instance_type: InstanceType | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceType',
        serialization_name='instanceType',
        shape_name='InstanceType',
    ))

    launch_time: _base.DateTime | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='LaunchTime',
        serialization_name='launchTime',
        shape_name='DateTime',
    ))

    placement: Placement | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Placement',
        serialization_name='placement',
        shape_name='Placement',
    ))

    kernel_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='KernelId',
        serialization_name='kernelId',
        shape_name='String',
    ))

    ramdisk_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RamdiskId',
        serialization_name='ramdiskId',
        shape_name='String',
    ))

    platform: PlatformValues | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Platform',
        serialization_name='platform',
        shape_name='PlatformValues',
    ))

    monitoring: Monitoring | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Monitoring',
        serialization_name='monitoring',
        shape_name='Monitoring',
    ))

    subnet_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SubnetId',
        serialization_name='subnetId',
        shape_name='String',
    ))

    vpc_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='VpcId',
        serialization_name='vpcId',
        shape_name='String',
    ))

    private_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        serialization_name='privateIpAddress',
        shape_name='String',
    ))

    public_ip_address: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='PublicIpAddress',
        serialization_name='ipAddress',
        shape_name='String',
    ))


InstanceTypeInfoList: _ta.TypeAlias = _ta.Sequence[InstanceTypeInfo]

SecurityGroupList: _ta.TypeAlias = _ta.Sequence[SecurityGroup]


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeInstanceTypesResult(
    _base.Shape,
    shape_name='DescribeInstanceTypesResult',
):
    instance_types: InstanceTypeInfoList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='InstanceTypes',
        serialization_name='instanceTypeSet',
        value_type=_base.ListValueType(InstanceTypeInfo),
        shape_name='InstanceTypeInfoList',
    ))

    next_token: NextToken | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='NextToken',
    ))


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeSecurityGroupsResult(
    _base.Shape,
    shape_name='DescribeSecurityGroupsResult',
):
    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))

    security_groups: SecurityGroupList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='SecurityGroups',
        serialization_name='securityGroupInfo',
        value_type=_base.ListValueType(SecurityGroup),
        shape_name='SecurityGroupList',
    ))


InstanceList: _ta.TypeAlias = _ta.Sequence[Instance]


@_dc.dataclass(frozen=True, kw_only=True)
class Reservation(
    _base.Shape,
    shape_name='Reservation',
):
    reservation_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='ReservationId',
        serialization_name='reservationId',
        shape_name='String',
    ))

    owner_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='OwnerId',
        serialization_name='ownerId',
        shape_name='String',
    ))

    requester_id: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='RequesterId',
        serialization_name='requesterId',
        shape_name='String',
    ))

    groups: GroupIdentifierList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Groups',
        serialization_name='groupSet',
        value_type=_base.ListValueType(GroupIdentifier),
        shape_name='GroupIdentifierList',
    ))

    instances: InstanceList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Instances',
        serialization_name='instancesSet',
        value_type=_base.ListValueType(Instance),
        shape_name='InstanceList',
    ))


ReservationList: _ta.TypeAlias = _ta.Sequence[Reservation]


@_dc.dataclass(frozen=True, kw_only=True)
class DescribeInstancesResult(
    _base.Shape,
    shape_name='DescribeInstancesResult',
):
    next_token: str | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='NextToken',
        serialization_name='nextToken',
        shape_name='String',
    ))

    reservations: ReservationList | None = _dc.field(default=None, metadata=_base.field_metadata(
        member_name='Reservations',
        serialization_name='reservationSet',
        value_type=_base.ListValueType(Reservation),
        shape_name='ReservationList',
    ))


ALL_SHAPES: frozenset[type[_base.Shape]] = frozenset([
    Address,
    AttachmentEnaSrdSpecification,
    AttachmentEnaSrdUdpSpecification,
    BlockDeviceMapping,
    BlockPublicAccessStates,
    CapacityReservationSpecification,
    CapacityReservationSpecificationResponse,
    CapacityReservationTarget,
    CapacityReservationTargetResponse,
    ConnectionTrackingConfiguration,
    ConnectionTrackingSpecificationRequest,
    ConnectionTrackingSpecificationResponse,
    CpuOptions,
    CpuOptionsRequest,
    CreateRouteRequest,
    CreateRouteResult,
    CreateRouteTableRequest,
    CreateRouteTableResult,
    CreateSecurityGroupRequest,
    CreateSecurityGroupResult,
    CreditSpecificationRequest,
    DeleteRouteRequest,
    DeleteRouteTableRequest,
    DeleteSecurityGroupRequest,
    DeleteSecurityGroupResult,
    DescribeAddressesRequest,
    DescribeAddressesResult,
    DescribeImagesRequest,
    DescribeImagesResult,
    DescribeInstanceTypesRequest,
    DescribeInstanceTypesResult,
    DescribeInstancesRequest,
    DescribeInstancesResult,
    DescribeInternetGatewaysRequest,
    DescribeInternetGatewaysResult,
    DescribeKeyPairsRequest,
    DescribeKeyPairsResult,
    DescribeNetworkInterfacesRequest,
    DescribeNetworkInterfacesResult,
    DescribeRouteTablesRequest,
    DescribeRouteTablesResult,
    DescribeSecurityGroupsRequest,
    DescribeSecurityGroupsResult,
    DescribeSubnetsRequest,
    DescribeSubnetsResult,
    DescribeVpcsRequest,
    DescribeVpcsResult,
    DiskInfo,
    EbsBlockDevice,
    EbsInfo,
    EbsInstanceBlockDevice,
    EbsOptimizedInfo,
    EfaInfo,
    ElasticGpuAssociation,
    ElasticGpuSpecification,
    ElasticInferenceAccelerator,
    ElasticInferenceAcceleratorAssociation,
    EnaSrdSpecificationRequest,
    EnaSrdUdpSpecificationRequest,
    EnclaveOptions,
    EnclaveOptionsRequest,
    Filter,
    FpgaDeviceInfo,
    FpgaDeviceMemoryInfo,
    FpgaInfo,
    GpuDeviceInfo,
    GpuDeviceMemoryInfo,
    GpuInfo,
    GroupIdentifier,
    HibernationOptions,
    HibernationOptionsRequest,
    IamInstanceProfile,
    IamInstanceProfileSpecification,
    Image,
    InferenceAcceleratorInfo,
    InferenceDeviceInfo,
    InferenceDeviceMemoryInfo,
    Instance,
    InstanceAttachmentEnaSrdSpecification,
    InstanceAttachmentEnaSrdUdpSpecification,
    InstanceBlockDeviceMapping,
    InstanceIpv4Prefix,
    InstanceIpv6Address,
    InstanceIpv6Prefix,
    InstanceMaintenanceOptions,
    InstanceMaintenanceOptionsRequest,
    InstanceMarketOptionsRequest,
    InstanceMetadataOptionsRequest,
    InstanceMetadataOptionsResponse,
    InstanceNetworkInterface,
    InstanceNetworkInterfaceAssociation,
    InstanceNetworkInterfaceAttachment,
    InstanceNetworkInterfaceSpecification,
    InstanceNetworkPerformanceOptions,
    InstanceNetworkPerformanceOptionsRequest,
    InstancePrivateIpAddress,
    InstanceState,
    InstanceStateChange,
    InstanceStorageInfo,
    InstanceTypeInfo,
    InternetGateway,
    InternetGatewayAttachment,
    IpPermission,
    IpRange,
    Ipv4PrefixSpecification,
    Ipv4PrefixSpecificationRequest,
    Ipv6PrefixSpecification,
    Ipv6PrefixSpecificationRequest,
    Ipv6Range,
    KeyPairInfo,
    LaunchTemplateSpecification,
    LicenseConfiguration,
    LicenseConfigurationRequest,
    MediaAcceleratorInfo,
    MediaDeviceInfo,
    MediaDeviceMemoryInfo,
    MemoryInfo,
    Monitoring,
    NetworkCardInfo,
    NetworkInfo,
    NetworkInterface,
    NetworkInterfaceAssociation,
    NetworkInterfaceAttachment,
    NetworkInterfaceIpv6Address,
    NetworkInterfacePrivateIpAddress,
    NeuronDeviceCoreInfo,
    NeuronDeviceInfo,
    NeuronDeviceMemoryInfo,
    NeuronInfo,
    NitroTpmInfo,
    OperatorRequest,
    OperatorResponse,
    Placement,
    PlacementGroupInfo,
    PrefixListId,
    PrivateDnsNameOptionsOnLaunch,
    PrivateDnsNameOptionsRequest,
    PrivateDnsNameOptionsResponse,
    PrivateIpAddressSpecification,
    ProcessorInfo,
    ProductCode,
    PropagatingVgw,
    RebootInstancesRequest,
    Reservation,
    Route,
    RouteTable,
    RouteTableAssociation,
    RouteTableAssociationState,
    RunInstancesMonitoringEnabled,
    RunInstancesRequest,
    SecurityGroup,
    SpotMarketOptions,
    StartInstancesRequest,
    StartInstancesResult,
    StateReason,
    StopInstancesRequest,
    StopInstancesResult,
    Subnet,
    SubnetCidrBlockState,
    SubnetIpv6CidrBlockAssociation,
    TagSpecification,
    TerminateInstancesRequest,
    TerminateInstancesResult,
    UserIdGroupPair,
    VCpuInfo,
    Vpc,
    VpcCidrBlockAssociation,
    VpcCidrBlockState,
    VpcEncryptionControl,
    VpcEncryptionControlExclusion,
    VpcEncryptionControlExclusions,
    VpcIpv6CidrBlockAssociation,
])


##


CREATE_ROUTE = _base.Operation(
    name='CreateRoute',
    input=CreateRouteRequest,
    output=CreateRouteResult,
)

CREATE_ROUTE_TABLE = _base.Operation(
    name='CreateRouteTable',
    input=CreateRouteTableRequest,
    output=CreateRouteTableResult,
)

CREATE_SECURITY_GROUP = _base.Operation(
    name='CreateSecurityGroup',
    input=CreateSecurityGroupRequest,
    output=CreateSecurityGroupResult,
)

DELETE_ROUTE = _base.Operation(
    name='DeleteRoute',
    input=DeleteRouteRequest,
)

DELETE_ROUTE_TABLE = _base.Operation(
    name='DeleteRouteTable',
    input=DeleteRouteTableRequest,
)

DELETE_SECURITY_GROUP = _base.Operation(
    name='DeleteSecurityGroup',
    input=DeleteSecurityGroupRequest,
    output=DeleteSecurityGroupResult,
)

DESCRIBE_ADDRESSES = _base.Operation(
    name='DescribeAddresses',
    input=DescribeAddressesRequest,
    output=DescribeAddressesResult,
)

DESCRIBE_IMAGES = _base.Operation(
    name='DescribeImages',
    input=DescribeImagesRequest,
    output=DescribeImagesResult,
)

DESCRIBE_INSTANCE_TYPES = _base.Operation(
    name='DescribeInstanceTypes',
    input=DescribeInstanceTypesRequest,
    output=DescribeInstanceTypesResult,
)

DESCRIBE_INSTANCES = _base.Operation(
    name='DescribeInstances',
    input=DescribeInstancesRequest,
    output=DescribeInstancesResult,
)

DESCRIBE_INTERNET_GATEWAYS = _base.Operation(
    name='DescribeInternetGateways',
    input=DescribeInternetGatewaysRequest,
    output=DescribeInternetGatewaysResult,
)

DESCRIBE_KEY_PAIRS = _base.Operation(
    name='DescribeKeyPairs',
    input=DescribeKeyPairsRequest,
    output=DescribeKeyPairsResult,
)

DESCRIBE_NETWORK_INTERFACES = _base.Operation(
    name='DescribeNetworkInterfaces',
    input=DescribeNetworkInterfacesRequest,
    output=DescribeNetworkInterfacesResult,
)

DESCRIBE_ROUTE_TABLES = _base.Operation(
    name='DescribeRouteTables',
    input=DescribeRouteTablesRequest,
    output=DescribeRouteTablesResult,
)

DESCRIBE_SECURITY_GROUPS = _base.Operation(
    name='DescribeSecurityGroups',
    input=DescribeSecurityGroupsRequest,
    output=DescribeSecurityGroupsResult,
)

DESCRIBE_SUBNETS = _base.Operation(
    name='DescribeSubnets',
    input=DescribeSubnetsRequest,
    output=DescribeSubnetsResult,
)

DESCRIBE_VPCS = _base.Operation(
    name='DescribeVpcs',
    input=DescribeVpcsRequest,
    output=DescribeVpcsResult,
)

REBOOT_INSTANCES = _base.Operation(
    name='RebootInstances',
    input=RebootInstancesRequest,
)

RUN_INSTANCES = _base.Operation(
    name='RunInstances',
    input=RunInstancesRequest,
    output=Reservation,
)

START_INSTANCES = _base.Operation(
    name='StartInstances',
    input=StartInstancesRequest,
    output=StartInstancesResult,
)

STOP_INSTANCES = _base.Operation(
    name='StopInstances',
    input=StopInstancesRequest,
    output=StopInstancesResult,
)

TERMINATE_INSTANCES = _base.Operation(
    name='TerminateInstances',
    input=TerminateInstancesRequest,
    output=TerminateInstancesResult,
)


ALL_OPERATIONS: frozenset[_base.Operation] = frozenset([
    CREATE_ROUTE,
    CREATE_ROUTE_TABLE,
    CREATE_SECURITY_GROUP,
    DELETE_ROUTE,
    DELETE_ROUTE_TABLE,
    DELETE_SECURITY_GROUP,
    DESCRIBE_ADDRESSES,
    DESCRIBE_IMAGES,
    DESCRIBE_INSTANCES,
    DESCRIBE_INSTANCE_TYPES,
    DESCRIBE_INTERNET_GATEWAYS,
    DESCRIBE_KEY_PAIRS,
    DESCRIBE_NETWORK_INTERFACES,
    DESCRIBE_ROUTE_TABLES,
    DESCRIBE_SECURITY_GROUPS,
    DESCRIBE_SUBNETS,
    DESCRIBE_VPCS,
    REBOOT_INSTANCES,
    RUN_INSTANCES,
    START_INSTANCES,
    STOP_INSTANCES,
    TERMINATE_INSTANCES,
])
