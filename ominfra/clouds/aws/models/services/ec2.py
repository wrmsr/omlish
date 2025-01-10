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


CoipPoolId = _ta.NewType('CoipPoolId', str)

CoreCount = _ta.NewType('CoreCount', int)

CpuManufacturerName = _ta.NewType('CpuManufacturerName', str)

CurrentGenerationFlag = _ta.NewType('CurrentGenerationFlag', bool)

DITMaxResults = _ta.NewType('DITMaxResults', int)

DedicatedHostFlag = _ta.NewType('DedicatedHostFlag', bool)

DefaultNetworkCardIndex = _ta.NewType('DefaultNetworkCardIndex', int)

DescribeInternetGatewaysMaxResults = _ta.NewType('DescribeInternetGatewaysMaxResults', int)

DescribeNetworkInterfacesMaxResults = _ta.NewType('DescribeNetworkInterfacesMaxResults', int)

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
    IPAM_RESOURCE_DISCOVERY = 'ipam-resource-discovery'
    IPAM_RESOURCE_DISCOVERY_ASSOCIATION = 'ipam-resource-discovery-association'
    INSTANCE_CONNECT_ENDPOINT = 'instance-connect-endpoint'
    VERIFIED_ACCESS_ENDPOINT_TARGET = 'verified-access-endpoint-target'
    IPAM_EXTERNAL_RESOURCE_VERIFICATION_TOKEN = 'ipam-external-resource-verification-token'


class RootDeviceType(_enum.Enum):
    EBS = 'ebs'
    INSTANCE_STORE = 'instance-store'


RunInstancesUserData = _ta.NewType('RunInstancesUserData', str)

SecurityGroupId = _ta.NewType('SecurityGroupId', str)

SecurityGroupName = _ta.NewType('SecurityGroupName', str)


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


VpcId = _ta.NewType('VpcId', str)


class VpcState(_enum.Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'


TotalFpgaMemory = _ta.NewType('TotalFpgaMemory', int)

TotalGpuMemory = _ta.NewType('TotalGpuMemory', int)

TotalInferenceMemory = _ta.NewType('TotalInferenceMemory', int)


@_dc.dataclass(frozen=True)
class Address(
    _base.Shape,
    shape_name='Address',
):
    allocation_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AllocationId',
        shape_name='String',
    ))

    association_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AssociationId',
        shape_name='String',
    ))

    domain: DomainType = _dc.field(metadata=_base.field_metadata(
        member_name='Domain',
        shape_name='DomainType',
    ))

    network_interface_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        shape_name='String',
    ))

    network_interface_owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaceOwnerId',
        shape_name='String',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))

    public_ipv4_pool: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicIpv4Pool',
        shape_name='String',
    ))

    network_border_group: str = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkBorderGroup',
        shape_name='String',
    ))

    customer_owned_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='CustomerOwnedIp',
        shape_name='String',
    ))

    customer_owned_ipv4_pool: str = _dc.field(metadata=_base.field_metadata(
        member_name='CustomerOwnedIpv4Pool',
        shape_name='String',
    ))

    carrier_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='CarrierIp',
        shape_name='String',
    ))

    instance_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceId',
        shape_name='String',
    ))

    public_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicIp',
        shape_name='String',
    ))


AllocationIdList: _ta.TypeAlias = _ta.Sequence[AllocationId]

ArchitectureTypeList: _ta.TypeAlias = _ta.Sequence[ArchitectureType]


@_dc.dataclass(frozen=True)
class AttachmentEnaSrdUdpSpecification(
    _base.Shape,
    shape_name='AttachmentEnaSrdUdpSpecification',
):
    ena_srd_udp_enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdUdpEnabled',
        shape_name='Boolean',
    ))


BandwidthWeightingTypeList: _ta.TypeAlias = _ta.Sequence[BandwidthWeightingType]


@_dc.dataclass(frozen=True)
class BlockPublicAccessStates(
    _base.Shape,
    shape_name='BlockPublicAccessStates',
):
    internet_gateway_block_mode: BlockPublicAccessMode = _dc.field(metadata=_base.field_metadata(
        member_name='InternetGatewayBlockMode',
        shape_name='BlockPublicAccessMode',
    ))


BootModeTypeList: _ta.TypeAlias = _ta.Sequence[BootModeType]


@_dc.dataclass(frozen=True)
class CapacityReservationTarget(
    _base.Shape,
    shape_name='CapacityReservationTarget',
):
    capacity_reservation_id: CapacityReservationId = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationId',
        shape_name='CapacityReservationId',
    ))

    capacity_reservation_resource_group_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationResourceGroupArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class CapacityReservationTargetResponse(
    _base.Shape,
    shape_name='CapacityReservationTargetResponse',
):
    capacity_reservation_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationId',
        shape_name='String',
    ))

    capacity_reservation_resource_group_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationResourceGroupArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class ConnectionTrackingConfiguration(
    _base.Shape,
    shape_name='ConnectionTrackingConfiguration',
):
    tcp_established_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='TcpEstablishedTimeout',
        shape_name='Integer',
    ))

    udp_stream_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='UdpStreamTimeout',
        shape_name='Integer',
    ))

    udp_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='UdpTimeout',
        shape_name='Integer',
    ))


@_dc.dataclass(frozen=True)
class ConnectionTrackingSpecificationRequest(
    _base.Shape,
    shape_name='ConnectionTrackingSpecificationRequest',
):
    tcp_established_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='TcpEstablishedTimeout',
        shape_name='Integer',
    ))

    udp_stream_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='UdpStreamTimeout',
        shape_name='Integer',
    ))

    udp_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='UdpTimeout',
        shape_name='Integer',
    ))


@_dc.dataclass(frozen=True)
class ConnectionTrackingSpecificationResponse(
    _base.Shape,
    shape_name='ConnectionTrackingSpecificationResponse',
):
    tcp_established_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='TcpEstablishedTimeout',
        shape_name='Integer',
    ))

    udp_stream_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='UdpStreamTimeout',
        shape_name='Integer',
    ))

    udp_timeout: int = _dc.field(metadata=_base.field_metadata(
        member_name='UdpTimeout',
        shape_name='Integer',
    ))


CoreCountList: _ta.TypeAlias = _ta.Sequence[CoreCount]


@_dc.dataclass(frozen=True)
class CpuOptions(
    _base.Shape,
    shape_name='CpuOptions',
):
    core_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='CoreCount',
        shape_name='Integer',
    ))

    threads_per_core: int = _dc.field(metadata=_base.field_metadata(
        member_name='ThreadsPerCore',
        shape_name='Integer',
    ))

    amd_sev_snp: AmdSevSnpSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='AmdSevSnp',
        shape_name='AmdSevSnpSpecification',
    ))


@_dc.dataclass(frozen=True)
class CpuOptionsRequest(
    _base.Shape,
    shape_name='CpuOptionsRequest',
):
    core_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='CoreCount',
        shape_name='Integer',
    ))

    threads_per_core: int = _dc.field(metadata=_base.field_metadata(
        member_name='ThreadsPerCore',
        shape_name='Integer',
    ))

    amd_sev_snp: AmdSevSnpSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='AmdSevSnp',
        shape_name='AmdSevSnpSpecification',
    ))


@_dc.dataclass(frozen=True)
class CreditSpecificationRequest(
    _base.Shape,
    shape_name='CreditSpecificationRequest',
):
    cpu_credits: str = _dc.field(metadata=_base.field_metadata(
        member_name='CpuCredits',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class DiskInfo(
    _base.Shape,
    shape_name='DiskInfo',
):
    size_in_g_b: DiskSize = _dc.field(metadata=_base.field_metadata(
        member_name='SizeInGB',
        shape_name='DiskSize',
    ))

    count: DiskCount = _dc.field(metadata=_base.field_metadata(
        member_name='Count',
        shape_name='DiskCount',
    ))

    type: DiskType = _dc.field(metadata=_base.field_metadata(
        member_name='Type',
        shape_name='DiskType',
    ))


@_dc.dataclass(frozen=True)
class EbsBlockDevice(
    _base.Shape,
    shape_name='EbsBlockDevice',
):
    delete_on_termination: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        shape_name='Boolean',
    ))

    iops: int = _dc.field(metadata=_base.field_metadata(
        member_name='Iops',
        shape_name='Integer',
    ))

    snapshot_id: SnapshotId = _dc.field(metadata=_base.field_metadata(
        member_name='SnapshotId',
        shape_name='SnapshotId',
    ))

    volume_size: int = _dc.field(metadata=_base.field_metadata(
        member_name='VolumeSize',
        shape_name='Integer',
    ))

    volume_type: VolumeType = _dc.field(metadata=_base.field_metadata(
        member_name='VolumeType',
        shape_name='VolumeType',
    ))

    kms_key_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='KmsKeyId',
        shape_name='String',
    ))

    throughput: int = _dc.field(metadata=_base.field_metadata(
        member_name='Throughput',
        shape_name='Integer',
    ))

    outpost_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='OutpostArn',
        shape_name='String',
    ))

    encrypted: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Encrypted',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class EbsOptimizedInfo(
    _base.Shape,
    shape_name='EbsOptimizedInfo',
):
    baseline_bandwidth_in_mbps: BaselineBandwidthInMbps = _dc.field(metadata=_base.field_metadata(
        member_name='BaselineBandwidthInMbps',
        shape_name='BaselineBandwidthInMbps',
    ))

    baseline_throughput_in_m_bps: BaselineThroughputInMBps = _dc.field(metadata=_base.field_metadata(
        member_name='BaselineThroughputInMBps',
        shape_name='BaselineThroughputInMBps',
    ))

    baseline_iops: BaselineIops = _dc.field(metadata=_base.field_metadata(
        member_name='BaselineIops',
        shape_name='BaselineIops',
    ))

    maximum_bandwidth_in_mbps: MaximumBandwidthInMbps = _dc.field(metadata=_base.field_metadata(
        member_name='MaximumBandwidthInMbps',
        shape_name='MaximumBandwidthInMbps',
    ))

    maximum_throughput_in_m_bps: MaximumThroughputInMBps = _dc.field(metadata=_base.field_metadata(
        member_name='MaximumThroughputInMBps',
        shape_name='MaximumThroughputInMBps',
    ))

    maximum_iops: MaximumIops = _dc.field(metadata=_base.field_metadata(
        member_name='MaximumIops',
        shape_name='MaximumIops',
    ))


@_dc.dataclass(frozen=True)
class EfaInfo(
    _base.Shape,
    shape_name='EfaInfo',
):
    maximum_efa_interfaces: MaximumEfaInterfaces = _dc.field(metadata=_base.field_metadata(
        member_name='MaximumEfaInterfaces',
        shape_name='MaximumEfaInterfaces',
    ))


@_dc.dataclass(frozen=True)
class ElasticGpuAssociation(
    _base.Shape,
    shape_name='ElasticGpuAssociation',
):
    elastic_gpu_id: ElasticGpuId = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticGpuId',
        shape_name='ElasticGpuId',
    ))

    elastic_gpu_association_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticGpuAssociationId',
        shape_name='String',
    ))

    elastic_gpu_association_state: str = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticGpuAssociationState',
        shape_name='String',
    ))

    elastic_gpu_association_time: str = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticGpuAssociationTime',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class ElasticGpuSpecification(
    _base.Shape,
    shape_name='ElasticGpuSpecification',
):
    type: str = _dc.field(metadata=_base.field_metadata(
        member_name='Type',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class ElasticInferenceAccelerator(
    _base.Shape,
    shape_name='ElasticInferenceAccelerator',
):
    type: str = _dc.field(metadata=_base.field_metadata(
        member_name='Type',
        shape_name='String',
    ))

    count: ElasticInferenceAcceleratorCount = _dc.field(metadata=_base.field_metadata(
        member_name='Count',
        shape_name='ElasticInferenceAcceleratorCount',
    ))


@_dc.dataclass(frozen=True)
class ElasticInferenceAcceleratorAssociation(
    _base.Shape,
    shape_name='ElasticInferenceAcceleratorAssociation',
):
    elastic_inference_accelerator_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorArn',
        shape_name='String',
    ))

    elastic_inference_accelerator_association_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorAssociationId',
        shape_name='String',
    ))

    elastic_inference_accelerator_association_state: str = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorAssociationState',
        shape_name='String',
    ))

    elastic_inference_accelerator_association_time: _base.DateTime = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorAssociationTime',
        shape_name='DateTime',
    ))


@_dc.dataclass(frozen=True)
class EnaSrdUdpSpecificationRequest(
    _base.Shape,
    shape_name='EnaSrdUdpSpecificationRequest',
):
    ena_srd_udp_enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdUdpEnabled',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class EnclaveOptions(
    _base.Shape,
    shape_name='EnclaveOptions',
):
    enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Enabled',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class EnclaveOptionsRequest(
    _base.Shape,
    shape_name='EnclaveOptionsRequest',
):
    enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Enabled',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class FpgaDeviceMemoryInfo(
    _base.Shape,
    shape_name='FpgaDeviceMemoryInfo',
):
    size_in_mi_b: FpgaDeviceMemorySize = _dc.field(metadata=_base.field_metadata(
        member_name='SizeInMiB',
        shape_name='FpgaDeviceMemorySize',
    ))


@_dc.dataclass(frozen=True)
class GpuDeviceMemoryInfo(
    _base.Shape,
    shape_name='GpuDeviceMemoryInfo',
):
    size_in_mi_b: GpuDeviceMemorySize = _dc.field(metadata=_base.field_metadata(
        member_name='SizeInMiB',
        shape_name='GpuDeviceMemorySize',
    ))


GroupIdStringList: _ta.TypeAlias = _ta.Sequence[SecurityGroupId]


@_dc.dataclass(frozen=True)
class GroupIdentifier(
    _base.Shape,
    shape_name='GroupIdentifier',
):
    group_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='GroupId',
        shape_name='String',
    ))

    group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='GroupName',
        shape_name='String',
    ))


GroupNameStringList: _ta.TypeAlias = _ta.Sequence[SecurityGroupName]


@_dc.dataclass(frozen=True)
class HibernationOptions(
    _base.Shape,
    shape_name='HibernationOptions',
):
    configured: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Configured',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class HibernationOptionsRequest(
    _base.Shape,
    shape_name='HibernationOptionsRequest',
):
    configured: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Configured',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class IamInstanceProfile(
    _base.Shape,
    shape_name='IamInstanceProfile',
):
    arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='Arn',
        shape_name='String',
    ))

    id: str = _dc.field(metadata=_base.field_metadata(
        member_name='Id',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class IamInstanceProfileSpecification(
    _base.Shape,
    shape_name='IamInstanceProfileSpecification',
):
    arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='Arn',
        shape_name='String',
    ))

    name: str = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class InferenceDeviceMemoryInfo(
    _base.Shape,
    shape_name='InferenceDeviceMemoryInfo',
):
    size_in_mi_b: InferenceDeviceMemorySize = _dc.field(metadata=_base.field_metadata(
        member_name='SizeInMiB',
        shape_name='InferenceDeviceMemorySize',
    ))


@_dc.dataclass(frozen=True)
class InstanceAttachmentEnaSrdUdpSpecification(
    _base.Shape,
    shape_name='InstanceAttachmentEnaSrdUdpSpecification',
):
    ena_srd_udp_enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdUdpEnabled',
        shape_name='Boolean',
    ))


InstanceIdStringList: _ta.TypeAlias = _ta.Sequence[InstanceId]


@_dc.dataclass(frozen=True)
class InstanceIpv4Prefix(
    _base.Shape,
    shape_name='InstanceIpv4Prefix',
):
    ipv4_prefix: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv4Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class InstanceIpv6Address(
    _base.Shape,
    shape_name='InstanceIpv6Address',
):
    ipv6_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Address',
        shape_name='String',
    ))

    is_primary_ipv6: bool = _dc.field(metadata=_base.field_metadata(
        member_name='IsPrimaryIpv6',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class InstanceIpv6Prefix(
    _base.Shape,
    shape_name='InstanceIpv6Prefix',
):
    ipv6_prefix: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class InstanceMaintenanceOptions(
    _base.Shape,
    shape_name='InstanceMaintenanceOptions',
):
    auto_recovery: InstanceAutoRecoveryState = _dc.field(metadata=_base.field_metadata(
        member_name='AutoRecovery',
        shape_name='InstanceAutoRecoveryState',
    ))


@_dc.dataclass(frozen=True)
class InstanceMaintenanceOptionsRequest(
    _base.Shape,
    shape_name='InstanceMaintenanceOptionsRequest',
):
    auto_recovery: InstanceAutoRecoveryState = _dc.field(metadata=_base.field_metadata(
        member_name='AutoRecovery',
        shape_name='InstanceAutoRecoveryState',
    ))


@_dc.dataclass(frozen=True)
class InstanceMetadataOptionsRequest(
    _base.Shape,
    shape_name='InstanceMetadataOptionsRequest',
):
    http_tokens: HttpTokensState = _dc.field(metadata=_base.field_metadata(
        member_name='HttpTokens',
        shape_name='HttpTokensState',
    ))

    http_put_response_hop_limit: int = _dc.field(metadata=_base.field_metadata(
        member_name='HttpPutResponseHopLimit',
        shape_name='Integer',
    ))

    http_endpoint: InstanceMetadataEndpointState = _dc.field(metadata=_base.field_metadata(
        member_name='HttpEndpoint',
        shape_name='InstanceMetadataEndpointState',
    ))

    http_protocol_ipv6: InstanceMetadataProtocolState = _dc.field(metadata=_base.field_metadata(
        member_name='HttpProtocolIpv6',
        shape_name='InstanceMetadataProtocolState',
    ))

    instance_metadata_tags: InstanceMetadataTagsState = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceMetadataTags',
        shape_name='InstanceMetadataTagsState',
    ))


@_dc.dataclass(frozen=True)
class InstanceMetadataOptionsResponse(
    _base.Shape,
    shape_name='InstanceMetadataOptionsResponse',
):
    state: InstanceMetadataOptionsState = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='InstanceMetadataOptionsState',
    ))

    http_tokens: HttpTokensState = _dc.field(metadata=_base.field_metadata(
        member_name='HttpTokens',
        shape_name='HttpTokensState',
    ))

    http_put_response_hop_limit: int = _dc.field(metadata=_base.field_metadata(
        member_name='HttpPutResponseHopLimit',
        shape_name='Integer',
    ))

    http_endpoint: InstanceMetadataEndpointState = _dc.field(metadata=_base.field_metadata(
        member_name='HttpEndpoint',
        shape_name='InstanceMetadataEndpointState',
    ))

    http_protocol_ipv6: InstanceMetadataProtocolState = _dc.field(metadata=_base.field_metadata(
        member_name='HttpProtocolIpv6',
        shape_name='InstanceMetadataProtocolState',
    ))

    instance_metadata_tags: InstanceMetadataTagsState = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceMetadataTags',
        shape_name='InstanceMetadataTagsState',
    ))


@_dc.dataclass(frozen=True)
class InstanceNetworkInterfaceAssociation(
    _base.Shape,
    shape_name='InstanceNetworkInterfaceAssociation',
):
    carrier_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='CarrierIp',
        shape_name='String',
    ))

    customer_owned_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='CustomerOwnedIp',
        shape_name='String',
    ))

    ip_owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='IpOwnerId',
        shape_name='String',
    ))

    public_dns_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicDnsName',
        shape_name='String',
    ))

    public_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicIp',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class InstanceNetworkPerformanceOptions(
    _base.Shape,
    shape_name='InstanceNetworkPerformanceOptions',
):
    bandwidth_weighting: InstanceBandwidthWeighting = _dc.field(metadata=_base.field_metadata(
        member_name='BandwidthWeighting',
        shape_name='InstanceBandwidthWeighting',
    ))


@_dc.dataclass(frozen=True)
class InstanceNetworkPerformanceOptionsRequest(
    _base.Shape,
    shape_name='InstanceNetworkPerformanceOptionsRequest',
):
    bandwidth_weighting: InstanceBandwidthWeighting = _dc.field(metadata=_base.field_metadata(
        member_name='BandwidthWeighting',
        shape_name='InstanceBandwidthWeighting',
    ))


@_dc.dataclass(frozen=True)
class InstanceState(
    _base.Shape,
    shape_name='InstanceState',
):
    code: int = _dc.field(metadata=_base.field_metadata(
        member_name='Code',
        shape_name='Integer',
    ))

    name: InstanceStateName = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='InstanceStateName',
    ))


@_dc.dataclass(frozen=True)
class InternetGatewayAttachment(
    _base.Shape,
    shape_name='InternetGatewayAttachment',
):
    state: AttachmentStatus = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='AttachmentStatus',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))


InternetGatewayIdList: _ta.TypeAlias = _ta.Sequence[InternetGatewayId]


@_dc.dataclass(frozen=True)
class IpRange(
    _base.Shape,
    shape_name='IpRange',
):
    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='String',
    ))

    cidr_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='CidrIp',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class Ipv4PrefixSpecification(
    _base.Shape,
    shape_name='Ipv4PrefixSpecification',
):
    ipv4_prefix: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv4Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class Ipv4PrefixSpecificationRequest(
    _base.Shape,
    shape_name='Ipv4PrefixSpecificationRequest',
):
    ipv4_prefix: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv4Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class Ipv6PrefixSpecification(
    _base.Shape,
    shape_name='Ipv6PrefixSpecification',
):
    ipv6_prefix: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class Ipv6PrefixSpecificationRequest(
    _base.Shape,
    shape_name='Ipv6PrefixSpecificationRequest',
):
    ipv6_prefix: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Prefix',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class Ipv6Range(
    _base.Shape,
    shape_name='Ipv6Range',
):
    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='String',
    ))

    cidr_ipv6: str = _dc.field(metadata=_base.field_metadata(
        member_name='CidrIpv6',
        shape_name='String',
    ))


KeyNameStringList: _ta.TypeAlias = _ta.Sequence[KeyPairName]

KeyPairIdStringList: _ta.TypeAlias = _ta.Sequence[KeyPairId]


@_dc.dataclass(frozen=True)
class KeyPairInfo(
    _base.Shape,
    shape_name='KeyPairInfo',
):
    key_pair_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='KeyPairId',
        shape_name='String',
    ))

    key_type: KeyType = _dc.field(metadata=_base.field_metadata(
        member_name='KeyType',
        shape_name='KeyType',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))

    public_key: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicKey',
        shape_name='String',
    ))

    create_time: _base.MillisecondDateTime = _dc.field(metadata=_base.field_metadata(
        member_name='CreateTime',
        shape_name='MillisecondDateTime',
    ))

    key_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='KeyName',
        shape_name='String',
    ))

    key_fingerprint: str = _dc.field(metadata=_base.field_metadata(
        member_name='KeyFingerprint',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class LaunchTemplateSpecification(
    _base.Shape,
    shape_name='LaunchTemplateSpecification',
):
    launch_template_id: LaunchTemplateId = _dc.field(metadata=_base.field_metadata(
        member_name='LaunchTemplateId',
        shape_name='LaunchTemplateId',
    ))

    launch_template_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='LaunchTemplateName',
        shape_name='String',
    ))

    version: str = _dc.field(metadata=_base.field_metadata(
        member_name='Version',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class LicenseConfiguration(
    _base.Shape,
    shape_name='LicenseConfiguration',
):
    license_configuration_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='LicenseConfigurationArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class LicenseConfigurationRequest(
    _base.Shape,
    shape_name='LicenseConfigurationRequest',
):
    license_configuration_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='LicenseConfigurationArn',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class MediaDeviceMemoryInfo(
    _base.Shape,
    shape_name='MediaDeviceMemoryInfo',
):
    size_in_mi_b: MediaDeviceMemorySize = _dc.field(metadata=_base.field_metadata(
        member_name='SizeInMiB',
        shape_name='MediaDeviceMemorySize',
    ))


@_dc.dataclass(frozen=True)
class MemoryInfo(
    _base.Shape,
    shape_name='MemoryInfo',
):
    size_in_mi_b: MemorySize = _dc.field(metadata=_base.field_metadata(
        member_name='SizeInMiB',
        shape_name='MemorySize',
    ))


@_dc.dataclass(frozen=True)
class Monitoring(
    _base.Shape,
    shape_name='Monitoring',
):
    state: MonitoringState = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='MonitoringState',
    ))


@_dc.dataclass(frozen=True)
class NetworkCardInfo(
    _base.Shape,
    shape_name='NetworkCardInfo',
):
    network_card_index: NetworkCardIndex = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkCardIndex',
        shape_name='NetworkCardIndex',
    ))

    network_performance: NetworkPerformance = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkPerformance',
        shape_name='NetworkPerformance',
    ))

    maximum_network_interfaces: MaxNetworkInterfaces = _dc.field(metadata=_base.field_metadata(
        member_name='MaximumNetworkInterfaces',
        shape_name='MaxNetworkInterfaces',
    ))

    baseline_bandwidth_in_gbps: BaselineBandwidthInGbps = _dc.field(metadata=_base.field_metadata(
        member_name='BaselineBandwidthInGbps',
        shape_name='BaselineBandwidthInGbps',
    ))

    peak_bandwidth_in_gbps: PeakBandwidthInGbps = _dc.field(metadata=_base.field_metadata(
        member_name='PeakBandwidthInGbps',
        shape_name='PeakBandwidthInGbps',
    ))


@_dc.dataclass(frozen=True)
class NetworkInterfaceAssociation(
    _base.Shape,
    shape_name='NetworkInterfaceAssociation',
):
    allocation_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AllocationId',
        shape_name='String',
    ))

    association_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AssociationId',
        shape_name='String',
    ))

    ip_owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='IpOwnerId',
        shape_name='String',
    ))

    public_dns_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicDnsName',
        shape_name='String',
    ))

    public_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicIp',
        shape_name='String',
    ))

    customer_owned_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='CustomerOwnedIp',
        shape_name='String',
    ))

    carrier_ip: str = _dc.field(metadata=_base.field_metadata(
        member_name='CarrierIp',
        shape_name='String',
    ))


NetworkInterfaceIdList: _ta.TypeAlias = _ta.Sequence[NetworkInterfaceId]


@_dc.dataclass(frozen=True)
class NetworkInterfaceIpv6Address(
    _base.Shape,
    shape_name='NetworkInterfaceIpv6Address',
):
    ipv6_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Address',
        shape_name='String',
    ))

    is_primary_ipv6: bool = _dc.field(metadata=_base.field_metadata(
        member_name='IsPrimaryIpv6',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class NeuronDeviceCoreInfo(
    _base.Shape,
    shape_name='NeuronDeviceCoreInfo',
):
    count: NeuronDeviceCoreCount = _dc.field(metadata=_base.field_metadata(
        member_name='Count',
        shape_name='NeuronDeviceCoreCount',
    ))

    version: NeuronDeviceCoreVersion = _dc.field(metadata=_base.field_metadata(
        member_name='Version',
        shape_name='NeuronDeviceCoreVersion',
    ))


@_dc.dataclass(frozen=True)
class NeuronDeviceMemoryInfo(
    _base.Shape,
    shape_name='NeuronDeviceMemoryInfo',
):
    size_in_mi_b: NeuronDeviceMemorySize = _dc.field(metadata=_base.field_metadata(
        member_name='SizeInMiB',
        shape_name='NeuronDeviceMemorySize',
    ))


NitroTpmSupportedVersionsList: _ta.TypeAlias = _ta.Sequence[NitroTpmSupportedVersionType]


@_dc.dataclass(frozen=True)
class OperatorRequest(
    _base.Shape,
    shape_name='OperatorRequest',
):
    principal: str = _dc.field(metadata=_base.field_metadata(
        member_name='Principal',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class OperatorResponse(
    _base.Shape,
    shape_name='OperatorResponse',
):
    managed: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Managed',
        shape_name='Boolean',
    ))

    principal: str = _dc.field(metadata=_base.field_metadata(
        member_name='Principal',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class Placement(
    _base.Shape,
    shape_name='Placement',
):
    affinity: str = _dc.field(metadata=_base.field_metadata(
        member_name='Affinity',
        shape_name='String',
    ))

    group_name: PlacementGroupName = _dc.field(metadata=_base.field_metadata(
        member_name='GroupName',
        shape_name='PlacementGroupName',
    ))

    partition_number: int = _dc.field(metadata=_base.field_metadata(
        member_name='PartitionNumber',
        shape_name='Integer',
    ))

    host_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='HostId',
        shape_name='String',
    ))

    tenancy: Tenancy = _dc.field(metadata=_base.field_metadata(
        member_name='Tenancy',
        shape_name='Tenancy',
    ))

    spread_domain: str = _dc.field(metadata=_base.field_metadata(
        member_name='SpreadDomain',
        shape_name='String',
    ))

    host_resource_group_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='HostResourceGroupArn',
        shape_name='String',
    ))

    group_id: PlacementGroupId = _dc.field(metadata=_base.field_metadata(
        member_name='GroupId',
        shape_name='PlacementGroupId',
    ))

    availability_zone: str = _dc.field(metadata=_base.field_metadata(
        member_name='AvailabilityZone',
        shape_name='String',
    ))


PlacementGroupStrategyList: _ta.TypeAlias = _ta.Sequence[PlacementGroupStrategy]


@_dc.dataclass(frozen=True)
class PrefixListId(
    _base.Shape,
    shape_name='PrefixListId',
):
    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='String',
    ))

    prefix_list_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrefixListId',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class PrivateDnsNameOptionsOnLaunch(
    _base.Shape,
    shape_name='PrivateDnsNameOptionsOnLaunch',
):
    hostname_type: HostnameType = _dc.field(metadata=_base.field_metadata(
        member_name='HostnameType',
        shape_name='HostnameType',
    ))

    enable_resource_name_dns_a_record: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsARecord',
        shape_name='Boolean',
    ))

    enable_resource_name_dns_aaaa_record: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsAAAARecord',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class PrivateDnsNameOptionsRequest(
    _base.Shape,
    shape_name='PrivateDnsNameOptionsRequest',
):
    hostname_type: HostnameType = _dc.field(metadata=_base.field_metadata(
        member_name='HostnameType',
        shape_name='HostnameType',
    ))

    enable_resource_name_dns_a_record: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsARecord',
        shape_name='Boolean',
    ))

    enable_resource_name_dns_aaaa_record: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsAAAARecord',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class PrivateDnsNameOptionsResponse(
    _base.Shape,
    shape_name='PrivateDnsNameOptionsResponse',
):
    hostname_type: HostnameType = _dc.field(metadata=_base.field_metadata(
        member_name='HostnameType',
        shape_name='HostnameType',
    ))

    enable_resource_name_dns_a_record: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsARecord',
        shape_name='Boolean',
    ))

    enable_resource_name_dns_aaaa_record: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsAAAARecord',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class PrivateIpAddressSpecification(
    _base.Shape,
    shape_name='PrivateIpAddressSpecification',
):
    primary: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Primary',
        shape_name='Boolean',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class ProductCode(
    _base.Shape,
    shape_name='ProductCode',
):
    product_code_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='ProductCodeId',
        shape_name='String',
    ))

    product_code_type: ProductCodeValues = _dc.field(metadata=_base.field_metadata(
        member_name='ProductCodeType',
        shape_name='ProductCodeValues',
    ))


PublicIpStringList: _ta.TypeAlias = _ta.Sequence[str]

RequestInstanceTypeList: _ta.TypeAlias = _ta.Sequence[InstanceType]

RootDeviceTypeList: _ta.TypeAlias = _ta.Sequence[RootDeviceType]


@_dc.dataclass(frozen=True)
class RunInstancesMonitoringEnabled(
    _base.Shape,
    shape_name='RunInstancesMonitoringEnabled',
):
    enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Enabled',
        shape_name='Boolean',
    ))


SecurityGroupIdStringList: _ta.TypeAlias = _ta.Sequence[SecurityGroupId]

SecurityGroupStringList: _ta.TypeAlias = _ta.Sequence[SecurityGroupName]


@_dc.dataclass(frozen=True)
class SpotMarketOptions(
    _base.Shape,
    shape_name='SpotMarketOptions',
):
    max_price: str = _dc.field(metadata=_base.field_metadata(
        member_name='MaxPrice',
        shape_name='String',
    ))

    spot_instance_type: SpotInstanceType = _dc.field(metadata=_base.field_metadata(
        member_name='SpotInstanceType',
        shape_name='SpotInstanceType',
    ))

    block_duration_minutes: int = _dc.field(metadata=_base.field_metadata(
        member_name='BlockDurationMinutes',
        shape_name='Integer',
    ))

    valid_until: _base.DateTime = _dc.field(metadata=_base.field_metadata(
        member_name='ValidUntil',
        shape_name='DateTime',
    ))

    instance_interruption_behavior: InstanceInterruptionBehavior = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceInterruptionBehavior',
        shape_name='InstanceInterruptionBehavior',
    ))


@_dc.dataclass(frozen=True)
class StateReason(
    _base.Shape,
    shape_name='StateReason',
):
    code: str = _dc.field(metadata=_base.field_metadata(
        member_name='Code',
        shape_name='String',
    ))

    message: str = _dc.field(metadata=_base.field_metadata(
        member_name='Message',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class SubnetCidrBlockState(
    _base.Shape,
    shape_name='SubnetCidrBlockState',
):
    state: SubnetCidrBlockStateCode = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='SubnetCidrBlockStateCode',
    ))

    status_message: str = _dc.field(metadata=_base.field_metadata(
        member_name='StatusMessage',
        shape_name='String',
    ))


SubnetIdStringList: _ta.TypeAlias = _ta.Sequence[SubnetId]

SupportedAdditionalProcessorFeatureList: _ta.TypeAlias = _ta.Sequence[SupportedAdditionalProcessorFeature]


@_dc.dataclass(frozen=True)
class TagSpecification(
    _base.Shape,
    shape_name='TagSpecification',
):
    resource_type: ResourceType = _dc.field(metadata=_base.field_metadata(
        member_name='ResourceType',
        shape_name='ResourceType',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))


ThreadsPerCoreList: _ta.TypeAlias = _ta.Sequence[ThreadsPerCore]

UsageClassTypeList: _ta.TypeAlias = _ta.Sequence[UsageClassType]


@_dc.dataclass(frozen=True)
class UserIdGroupPair(
    _base.Shape,
    shape_name='UserIdGroupPair',
):
    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='String',
    ))

    user_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='UserId',
        shape_name='String',
    ))

    group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='GroupName',
        shape_name='String',
    ))

    group_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='GroupId',
        shape_name='String',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))

    vpc_peering_connection_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcPeeringConnectionId',
        shape_name='String',
    ))

    peering_status: str = _dc.field(metadata=_base.field_metadata(
        member_name='PeeringStatus',
        shape_name='String',
    ))


ValueStringList: _ta.TypeAlias = _ta.Sequence[str]

VirtualizationTypeList: _ta.TypeAlias = _ta.Sequence[VirtualizationType]


@_dc.dataclass(frozen=True)
class VpcCidrBlockState(
    _base.Shape,
    shape_name='VpcCidrBlockState',
):
    state: VpcCidrBlockStateCode = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='VpcCidrBlockStateCode',
    ))

    status_message: str = _dc.field(metadata=_base.field_metadata(
        member_name='StatusMessage',
        shape_name='String',
    ))


VpcIdStringList: _ta.TypeAlias = _ta.Sequence[VpcId]

AddressList: _ta.TypeAlias = _ta.Sequence[Address]


@_dc.dataclass(frozen=True)
class AttachmentEnaSrdSpecification(
    _base.Shape,
    shape_name='AttachmentEnaSrdSpecification',
):
    ena_srd_enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdEnabled',
        shape_name='Boolean',
    ))

    ena_srd_udp_specification: AttachmentEnaSrdUdpSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdUdpSpecification',
        shape_name='AttachmentEnaSrdUdpSpecification',
    ))


@_dc.dataclass(frozen=True)
class BlockDeviceMapping(
    _base.Shape,
    shape_name='BlockDeviceMapping',
):
    ebs: EbsBlockDevice = _dc.field(metadata=_base.field_metadata(
        member_name='Ebs',
        shape_name='EbsBlockDevice',
    ))

    no_device: str = _dc.field(metadata=_base.field_metadata(
        member_name='NoDevice',
        shape_name='String',
    ))

    device_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DeviceName',
        shape_name='String',
    ))

    virtual_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='VirtualName',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class CapacityReservationSpecification(
    _base.Shape,
    shape_name='CapacityReservationSpecification',
):
    capacity_reservation_preference: CapacityReservationPreference = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationPreference',
        shape_name='CapacityReservationPreference',
    ))

    capacity_reservation_target: CapacityReservationTarget = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationTarget',
        shape_name='CapacityReservationTarget',
    ))


@_dc.dataclass(frozen=True)
class CapacityReservationSpecificationResponse(
    _base.Shape,
    shape_name='CapacityReservationSpecificationResponse',
):
    capacity_reservation_preference: CapacityReservationPreference = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationPreference',
        shape_name='CapacityReservationPreference',
    ))

    capacity_reservation_target: CapacityReservationTargetResponse = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationTarget',
        shape_name='CapacityReservationTargetResponse',
    ))


DiskInfoList: _ta.TypeAlias = _ta.Sequence[DiskInfo]


@_dc.dataclass(frozen=True)
class EbsInfo(
    _base.Shape,
    shape_name='EbsInfo',
):
    ebs_optimized_support: EbsOptimizedSupport = _dc.field(metadata=_base.field_metadata(
        member_name='EbsOptimizedSupport',
        shape_name='EbsOptimizedSupport',
    ))

    encryption_support: EbsEncryptionSupport = _dc.field(metadata=_base.field_metadata(
        member_name='EncryptionSupport',
        shape_name='EbsEncryptionSupport',
    ))

    ebs_optimized_info: EbsOptimizedInfo = _dc.field(metadata=_base.field_metadata(
        member_name='EbsOptimizedInfo',
        shape_name='EbsOptimizedInfo',
    ))

    nvme_support: EbsNvmeSupport = _dc.field(metadata=_base.field_metadata(
        member_name='NvmeSupport',
        shape_name='EbsNvmeSupport',
    ))


@_dc.dataclass(frozen=True)
class EbsInstanceBlockDevice(
    _base.Shape,
    shape_name='EbsInstanceBlockDevice',
):
    attach_time: _base.DateTime = _dc.field(metadata=_base.field_metadata(
        member_name='AttachTime',
        shape_name='DateTime',
    ))

    delete_on_termination: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        shape_name='Boolean',
    ))

    status: AttachmentStatus = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='AttachmentStatus',
    ))

    volume_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VolumeId',
        shape_name='String',
    ))

    associated_resource: str = _dc.field(metadata=_base.field_metadata(
        member_name='AssociatedResource',
        shape_name='String',
    ))

    volume_owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VolumeOwnerId',
        shape_name='String',
    ))

    operator: OperatorResponse = _dc.field(metadata=_base.field_metadata(
        member_name='Operator',
        shape_name='OperatorResponse',
    ))


ElasticGpuAssociationList: _ta.TypeAlias = _ta.Sequence[ElasticGpuAssociation]

ElasticGpuSpecifications: _ta.TypeAlias = _ta.Sequence[ElasticGpuSpecification]

ElasticInferenceAcceleratorAssociationList: _ta.TypeAlias = _ta.Sequence[ElasticInferenceAcceleratorAssociation]

ElasticInferenceAccelerators: _ta.TypeAlias = _ta.Sequence[ElasticInferenceAccelerator]


@_dc.dataclass(frozen=True)
class EnaSrdSpecificationRequest(
    _base.Shape,
    shape_name='EnaSrdSpecificationRequest',
):
    ena_srd_enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdEnabled',
        shape_name='Boolean',
    ))

    ena_srd_udp_specification: EnaSrdUdpSpecificationRequest = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdUdpSpecification',
        shape_name='EnaSrdUdpSpecificationRequest',
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

    values: ValueStringList = _dc.field(metadata=_base.field_metadata(
        member_name='Values',
        shape_name='ValueStringList',
    ))


@_dc.dataclass(frozen=True)
class FpgaDeviceInfo(
    _base.Shape,
    shape_name='FpgaDeviceInfo',
):
    name: FpgaDeviceName = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='FpgaDeviceName',
    ))

    manufacturer: FpgaDeviceManufacturerName = _dc.field(metadata=_base.field_metadata(
        member_name='Manufacturer',
        shape_name='FpgaDeviceManufacturerName',
    ))

    count: FpgaDeviceCount = _dc.field(metadata=_base.field_metadata(
        member_name='Count',
        shape_name='FpgaDeviceCount',
    ))

    memory_info: FpgaDeviceMemoryInfo = _dc.field(metadata=_base.field_metadata(
        member_name='MemoryInfo',
        shape_name='FpgaDeviceMemoryInfo',
    ))


@_dc.dataclass(frozen=True)
class GpuDeviceInfo(
    _base.Shape,
    shape_name='GpuDeviceInfo',
):
    name: GpuDeviceName = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='GpuDeviceName',
    ))

    manufacturer: GpuDeviceManufacturerName = _dc.field(metadata=_base.field_metadata(
        member_name='Manufacturer',
        shape_name='GpuDeviceManufacturerName',
    ))

    count: GpuDeviceCount = _dc.field(metadata=_base.field_metadata(
        member_name='Count',
        shape_name='GpuDeviceCount',
    ))

    memory_info: GpuDeviceMemoryInfo = _dc.field(metadata=_base.field_metadata(
        member_name='MemoryInfo',
        shape_name='GpuDeviceMemoryInfo',
    ))


GroupIdentifierList: _ta.TypeAlias = _ta.Sequence[GroupIdentifier]


@_dc.dataclass(frozen=True)
class InferenceDeviceInfo(
    _base.Shape,
    shape_name='InferenceDeviceInfo',
):
    count: InferenceDeviceCount = _dc.field(metadata=_base.field_metadata(
        member_name='Count',
        shape_name='InferenceDeviceCount',
    ))

    name: InferenceDeviceName = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='InferenceDeviceName',
    ))

    manufacturer: InferenceDeviceManufacturerName = _dc.field(metadata=_base.field_metadata(
        member_name='Manufacturer',
        shape_name='InferenceDeviceManufacturerName',
    ))

    memory_info: InferenceDeviceMemoryInfo = _dc.field(metadata=_base.field_metadata(
        member_name='MemoryInfo',
        shape_name='InferenceDeviceMemoryInfo',
    ))


@_dc.dataclass(frozen=True)
class InstanceAttachmentEnaSrdSpecification(
    _base.Shape,
    shape_name='InstanceAttachmentEnaSrdSpecification',
):
    ena_srd_enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdEnabled',
        shape_name='Boolean',
    ))

    ena_srd_udp_specification: InstanceAttachmentEnaSrdUdpSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdUdpSpecification',
        shape_name='InstanceAttachmentEnaSrdUdpSpecification',
    ))


InstanceIpv4PrefixList: _ta.TypeAlias = _ta.Sequence[InstanceIpv4Prefix]

InstanceIpv6AddressList: _ta.TypeAlias = _ta.Sequence[InstanceIpv6Address]

InstanceIpv6PrefixList: _ta.TypeAlias = _ta.Sequence[InstanceIpv6Prefix]


@_dc.dataclass(frozen=True)
class InstanceMarketOptionsRequest(
    _base.Shape,
    shape_name='InstanceMarketOptionsRequest',
):
    market_type: MarketType = _dc.field(metadata=_base.field_metadata(
        member_name='MarketType',
        shape_name='MarketType',
    ))

    spot_options: SpotMarketOptions = _dc.field(metadata=_base.field_metadata(
        member_name='SpotOptions',
        shape_name='SpotMarketOptions',
    ))


@_dc.dataclass(frozen=True)
class InstancePrivateIpAddress(
    _base.Shape,
    shape_name='InstancePrivateIpAddress',
):
    association: InstanceNetworkInterfaceAssociation = _dc.field(metadata=_base.field_metadata(
        member_name='Association',
        shape_name='InstanceNetworkInterfaceAssociation',
    ))

    primary: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Primary',
        shape_name='Boolean',
    ))

    private_dns_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        shape_name='String',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class InstanceStateChange(
    _base.Shape,
    shape_name='InstanceStateChange',
):
    instance_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceId',
        shape_name='String',
    ))

    current_state: InstanceState = _dc.field(metadata=_base.field_metadata(
        member_name='CurrentState',
        shape_name='InstanceState',
    ))

    previous_state: InstanceState = _dc.field(metadata=_base.field_metadata(
        member_name='PreviousState',
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


@_dc.dataclass(frozen=True)
class MediaDeviceInfo(
    _base.Shape,
    shape_name='MediaDeviceInfo',
):
    count: MediaDeviceCount = _dc.field(metadata=_base.field_metadata(
        member_name='Count',
        shape_name='MediaDeviceCount',
    ))

    name: MediaDeviceName = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='MediaDeviceName',
    ))

    manufacturer: MediaDeviceManufacturerName = _dc.field(metadata=_base.field_metadata(
        member_name='Manufacturer',
        shape_name='MediaDeviceManufacturerName',
    ))

    memory_info: MediaDeviceMemoryInfo = _dc.field(metadata=_base.field_metadata(
        member_name='MemoryInfo',
        shape_name='MediaDeviceMemoryInfo',
    ))


NetworkCardInfoList: _ta.TypeAlias = _ta.Sequence[NetworkCardInfo]

NetworkInterfaceIpv6AddressesList: _ta.TypeAlias = _ta.Sequence[NetworkInterfaceIpv6Address]


@_dc.dataclass(frozen=True)
class NetworkInterfacePrivateIpAddress(
    _base.Shape,
    shape_name='NetworkInterfacePrivateIpAddress',
):
    association: NetworkInterfaceAssociation = _dc.field(metadata=_base.field_metadata(
        member_name='Association',
        shape_name='NetworkInterfaceAssociation',
    ))

    primary: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Primary',
        shape_name='Boolean',
    ))

    private_dns_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        shape_name='String',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class NeuronDeviceInfo(
    _base.Shape,
    shape_name='NeuronDeviceInfo',
):
    count: NeuronDeviceCount = _dc.field(metadata=_base.field_metadata(
        member_name='Count',
        shape_name='NeuronDeviceCount',
    ))

    name: NeuronDeviceName = _dc.field(metadata=_base.field_metadata(
        member_name='Name',
        shape_name='NeuronDeviceName',
    ))

    core_info: NeuronDeviceCoreInfo = _dc.field(metadata=_base.field_metadata(
        member_name='CoreInfo',
        shape_name='NeuronDeviceCoreInfo',
    ))

    memory_info: NeuronDeviceMemoryInfo = _dc.field(metadata=_base.field_metadata(
        member_name='MemoryInfo',
        shape_name='NeuronDeviceMemoryInfo',
    ))


@_dc.dataclass(frozen=True)
class NitroTpmInfo(
    _base.Shape,
    shape_name='NitroTpmInfo',
):
    supported_versions: NitroTpmSupportedVersionsList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedVersions',
        shape_name='NitroTpmSupportedVersionsList',
    ))


@_dc.dataclass(frozen=True)
class PlacementGroupInfo(
    _base.Shape,
    shape_name='PlacementGroupInfo',
):
    supported_strategies: PlacementGroupStrategyList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedStrategies',
        shape_name='PlacementGroupStrategyList',
    ))


PrefixListIdList: _ta.TypeAlias = _ta.Sequence[PrefixListId]

PrivateIpAddressSpecificationList: _ta.TypeAlias = _ta.Sequence[PrivateIpAddressSpecification]


@_dc.dataclass(frozen=True)
class ProcessorInfo(
    _base.Shape,
    shape_name='ProcessorInfo',
):
    supported_architectures: ArchitectureTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedArchitectures',
        shape_name='ArchitectureTypeList',
    ))

    sustained_clock_speed_in_ghz: ProcessorSustainedClockSpeed = _dc.field(metadata=_base.field_metadata(
        member_name='SustainedClockSpeedInGhz',
        shape_name='ProcessorSustainedClockSpeed',
    ))

    supported_features: SupportedAdditionalProcessorFeatureList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedFeatures',
        shape_name='SupportedAdditionalProcessorFeatureList',
    ))

    manufacturer: CpuManufacturerName = _dc.field(metadata=_base.field_metadata(
        member_name='Manufacturer',
        shape_name='CpuManufacturerName',
    ))


ProductCodeList: _ta.TypeAlias = _ta.Sequence[ProductCode]


@_dc.dataclass(frozen=True)
class RebootInstancesRequest(
    _base.Shape,
    shape_name='RebootInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        shape_name='InstanceIdStringList',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class StartInstancesRequest(
    _base.Shape,
    shape_name='StartInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        shape_name='InstanceIdStringList',
    ))

    additional_info: str = _dc.field(metadata=_base.field_metadata(
        member_name='AdditionalInfo',
        shape_name='String',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class StopInstancesRequest(
    _base.Shape,
    shape_name='StopInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        shape_name='InstanceIdStringList',
    ))

    hibernate: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Hibernate',
        shape_name='Boolean',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    force: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Force',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class SubnetIpv6CidrBlockAssociation(
    _base.Shape,
    shape_name='SubnetIpv6CidrBlockAssociation',
):
    association_id: SubnetCidrAssociationId = _dc.field(metadata=_base.field_metadata(
        member_name='AssociationId',
        shape_name='SubnetCidrAssociationId',
    ))

    ipv6_cidr_block: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6CidrBlock',
        shape_name='String',
    ))

    ipv6_cidr_block_state: SubnetCidrBlockState = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6CidrBlockState',
        shape_name='SubnetCidrBlockState',
    ))

    ipv6_address_attribute: Ipv6AddressAttribute = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6AddressAttribute',
        shape_name='Ipv6AddressAttribute',
    ))

    ip_source: IpSource = _dc.field(metadata=_base.field_metadata(
        member_name='IpSource',
        shape_name='IpSource',
    ))


TagSpecificationList: _ta.TypeAlias = _ta.Sequence[TagSpecification]


@_dc.dataclass(frozen=True)
class TerminateInstancesRequest(
    _base.Shape,
    shape_name='TerminateInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        shape_name='InstanceIdStringList',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))


UserIdGroupPairList: _ta.TypeAlias = _ta.Sequence[UserIdGroupPair]


@_dc.dataclass(frozen=True)
class VCpuInfo(
    _base.Shape,
    shape_name='VCpuInfo',
):
    default_v_cpus: VCpuCount = _dc.field(metadata=_base.field_metadata(
        member_name='DefaultVCpus',
        shape_name='VCpuCount',
    ))

    default_cores: CoreCount = _dc.field(metadata=_base.field_metadata(
        member_name='DefaultCores',
        shape_name='CoreCount',
    ))

    default_threads_per_core: ThreadsPerCore = _dc.field(metadata=_base.field_metadata(
        member_name='DefaultThreadsPerCore',
        shape_name='ThreadsPerCore',
    ))

    valid_cores: CoreCountList = _dc.field(metadata=_base.field_metadata(
        member_name='ValidCores',
        shape_name='CoreCountList',
    ))

    valid_threads_per_core: ThreadsPerCoreList = _dc.field(metadata=_base.field_metadata(
        member_name='ValidThreadsPerCore',
        shape_name='ThreadsPerCoreList',
    ))


@_dc.dataclass(frozen=True)
class VpcCidrBlockAssociation(
    _base.Shape,
    shape_name='VpcCidrBlockAssociation',
):
    association_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AssociationId',
        shape_name='String',
    ))

    cidr_block: str = _dc.field(metadata=_base.field_metadata(
        member_name='CidrBlock',
        shape_name='String',
    ))

    cidr_block_state: VpcCidrBlockState = _dc.field(metadata=_base.field_metadata(
        member_name='CidrBlockState',
        shape_name='VpcCidrBlockState',
    ))


@_dc.dataclass(frozen=True)
class VpcIpv6CidrBlockAssociation(
    _base.Shape,
    shape_name='VpcIpv6CidrBlockAssociation',
):
    association_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AssociationId',
        shape_name='String',
    ))

    ipv6_cidr_block: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6CidrBlock',
        shape_name='String',
    ))

    ipv6_cidr_block_state: VpcCidrBlockState = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6CidrBlockState',
        shape_name='VpcCidrBlockState',
    ))

    network_border_group: str = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkBorderGroup',
        shape_name='String',
    ))

    ipv6_pool: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Pool',
        shape_name='String',
    ))

    ipv6_address_attribute: Ipv6AddressAttribute = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6AddressAttribute',
        shape_name='Ipv6AddressAttribute',
    ))

    ip_source: IpSource = _dc.field(metadata=_base.field_metadata(
        member_name='IpSource',
        shape_name='IpSource',
    ))


BlockDeviceMappingRequestList: _ta.TypeAlias = _ta.Sequence[BlockDeviceMapping]


@_dc.dataclass(frozen=True)
class DescribeAddressesResult(
    _base.Shape,
    shape_name='DescribeAddressesResult',
):
    addresses: AddressList = _dc.field(metadata=_base.field_metadata(
        member_name='Addresses',
        shape_name='AddressList',
    ))


@_dc.dataclass(frozen=True)
class DescribeKeyPairsResult(
    _base.Shape,
    shape_name='DescribeKeyPairsResult',
):
    key_pairs: KeyPairList = _dc.field(metadata=_base.field_metadata(
        member_name='KeyPairs',
        shape_name='KeyPairList',
    ))


FilterList: _ta.TypeAlias = _ta.Sequence[Filter]

FpgaDeviceInfoList: _ta.TypeAlias = _ta.Sequence[FpgaDeviceInfo]

GpuDeviceInfoList: _ta.TypeAlias = _ta.Sequence[GpuDeviceInfo]

InferenceDeviceInfoList: _ta.TypeAlias = _ta.Sequence[InferenceDeviceInfo]


@_dc.dataclass(frozen=True)
class InstanceBlockDeviceMapping(
    _base.Shape,
    shape_name='InstanceBlockDeviceMapping',
):
    device_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='DeviceName',
        shape_name='String',
    ))

    ebs: EbsInstanceBlockDevice = _dc.field(metadata=_base.field_metadata(
        member_name='Ebs',
        shape_name='EbsInstanceBlockDevice',
    ))


@_dc.dataclass(frozen=True)
class InstanceNetworkInterfaceAttachment(
    _base.Shape,
    shape_name='InstanceNetworkInterfaceAttachment',
):
    attach_time: _base.DateTime = _dc.field(metadata=_base.field_metadata(
        member_name='AttachTime',
        shape_name='DateTime',
    ))

    attachment_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AttachmentId',
        shape_name='String',
    ))

    delete_on_termination: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        shape_name='Boolean',
    ))

    device_index: int = _dc.field(metadata=_base.field_metadata(
        member_name='DeviceIndex',
        shape_name='Integer',
    ))

    status: AttachmentStatus = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='AttachmentStatus',
    ))

    network_card_index: int = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkCardIndex',
        shape_name='Integer',
    ))

    ena_srd_specification: InstanceAttachmentEnaSrdSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdSpecification',
        shape_name='InstanceAttachmentEnaSrdSpecification',
    ))


@_dc.dataclass(frozen=True)
class InstanceNetworkInterfaceSpecification(
    _base.Shape,
    shape_name='InstanceNetworkInterfaceSpecification',
):
    associate_public_ip_address: bool = _dc.field(metadata=_base.field_metadata(
        member_name='AssociatePublicIpAddress',
        shape_name='Boolean',
    ))

    delete_on_termination: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        shape_name='Boolean',
    ))

    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='String',
    ))

    device_index: int = _dc.field(metadata=_base.field_metadata(
        member_name='DeviceIndex',
        shape_name='Integer',
    ))

    groups: SecurityGroupIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='Groups',
        shape_name='SecurityGroupIdStringList',
    ))

    ipv6_address_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6AddressCount',
        shape_name='Integer',
    ))

    ipv6_addresses: InstanceIpv6AddressList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Addresses',
        shape_name='InstanceIpv6AddressList',
    ))

    network_interface_id: NetworkInterfaceId = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        shape_name='NetworkInterfaceId',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))

    private_ip_addresses: PrivateIpAddressSpecificationList = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddresses',
        shape_name='PrivateIpAddressSpecificationList',
    ))

    secondary_private_ip_address_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='SecondaryPrivateIpAddressCount',
        shape_name='Integer',
    ))

    subnet_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetId',
        shape_name='String',
    ))

    associate_carrier_ip_address: bool = _dc.field(metadata=_base.field_metadata(
        member_name='AssociateCarrierIpAddress',
        shape_name='Boolean',
    ))

    interface_type: str = _dc.field(metadata=_base.field_metadata(
        member_name='InterfaceType',
        shape_name='String',
    ))

    network_card_index: int = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkCardIndex',
        shape_name='Integer',
    ))

    ipv4_prefixes: Ipv4PrefixList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv4Prefixes',
        shape_name='Ipv4PrefixList',
    ))

    ipv4_prefix_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv4PrefixCount',
        shape_name='Integer',
    ))

    ipv6_prefixes: Ipv6PrefixList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Prefixes',
        shape_name='Ipv6PrefixList',
    ))

    ipv6_prefix_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6PrefixCount',
        shape_name='Integer',
    ))

    primary_ipv6: bool = _dc.field(metadata=_base.field_metadata(
        member_name='PrimaryIpv6',
        shape_name='Boolean',
    ))

    ena_srd_specification: EnaSrdSpecificationRequest = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdSpecification',
        shape_name='EnaSrdSpecificationRequest',
    ))

    connection_tracking_specification: ConnectionTrackingSpecificationRequest = _dc.field(metadata=_base.field_metadata(
        member_name='ConnectionTrackingSpecification',
        shape_name='ConnectionTrackingSpecificationRequest',
    ))


InstancePrivateIpAddressList: _ta.TypeAlias = _ta.Sequence[InstancePrivateIpAddress]

InstanceStateChangeList: _ta.TypeAlias = _ta.Sequence[InstanceStateChange]


@_dc.dataclass(frozen=True)
class InstanceStorageInfo(
    _base.Shape,
    shape_name='InstanceStorageInfo',
):
    total_size_in_g_b: DiskSize = _dc.field(metadata=_base.field_metadata(
        member_name='TotalSizeInGB',
        shape_name='DiskSize',
    ))

    disks: DiskInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='Disks',
        shape_name='DiskInfoList',
    ))

    nvme_support: EphemeralNvmeSupport = _dc.field(metadata=_base.field_metadata(
        member_name='NvmeSupport',
        shape_name='EphemeralNvmeSupport',
    ))

    encryption_support: InstanceStorageEncryptionSupport = _dc.field(metadata=_base.field_metadata(
        member_name='EncryptionSupport',
        shape_name='InstanceStorageEncryptionSupport',
    ))


@_dc.dataclass(frozen=True)
class InternetGateway(
    _base.Shape,
    shape_name='InternetGateway',
):
    attachments: InternetGatewayAttachmentList = _dc.field(metadata=_base.field_metadata(
        member_name='Attachments',
        shape_name='InternetGatewayAttachmentList',
    ))

    internet_gateway_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='InternetGatewayId',
        shape_name='String',
    ))

    owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='OwnerId',
        shape_name='String',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))


@_dc.dataclass(frozen=True)
class IpPermission(
    _base.Shape,
    shape_name='IpPermission',
):
    ip_protocol: str = _dc.field(metadata=_base.field_metadata(
        member_name='IpProtocol',
        shape_name='String',
    ))

    from_port: int = _dc.field(metadata=_base.field_metadata(
        member_name='FromPort',
        shape_name='Integer',
    ))

    to_port: int = _dc.field(metadata=_base.field_metadata(
        member_name='ToPort',
        shape_name='Integer',
    ))

    user_id_group_pairs: UserIdGroupPairList = _dc.field(metadata=_base.field_metadata(
        member_name='UserIdGroupPairs',
        shape_name='UserIdGroupPairList',
    ))

    ip_ranges: IpRangeList = _dc.field(metadata=_base.field_metadata(
        member_name='IpRanges',
        shape_name='IpRangeList',
    ))

    ipv6_ranges: Ipv6RangeList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Ranges',
        shape_name='Ipv6RangeList',
    ))

    prefix_list_ids: PrefixListIdList = _dc.field(metadata=_base.field_metadata(
        member_name='PrefixListIds',
        shape_name='PrefixListIdList',
    ))


MediaDeviceInfoList: _ta.TypeAlias = _ta.Sequence[MediaDeviceInfo]


@_dc.dataclass(frozen=True)
class NetworkInfo(
    _base.Shape,
    shape_name='NetworkInfo',
):
    network_performance: NetworkPerformance = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkPerformance',
        shape_name='NetworkPerformance',
    ))

    maximum_network_interfaces: MaxNetworkInterfaces = _dc.field(metadata=_base.field_metadata(
        member_name='MaximumNetworkInterfaces',
        shape_name='MaxNetworkInterfaces',
    ))

    maximum_network_cards: MaximumNetworkCards = _dc.field(metadata=_base.field_metadata(
        member_name='MaximumNetworkCards',
        shape_name='MaximumNetworkCards',
    ))

    default_network_card_index: DefaultNetworkCardIndex = _dc.field(metadata=_base.field_metadata(
        member_name='DefaultNetworkCardIndex',
        shape_name='DefaultNetworkCardIndex',
    ))

    network_cards: NetworkCardInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkCards',
        shape_name='NetworkCardInfoList',
    ))

    ipv4_addresses_per_interface: MaxIpv4AddrPerInterface = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv4AddressesPerInterface',
        shape_name='MaxIpv4AddrPerInterface',
    ))

    ipv6_addresses_per_interface: MaxIpv6AddrPerInterface = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6AddressesPerInterface',
        shape_name='MaxIpv6AddrPerInterface',
    ))

    ipv6_supported: Ipv6Flag = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Supported',
        shape_name='Ipv6Flag',
    ))

    ena_support: EnaSupport = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSupport',
        shape_name='EnaSupport',
    ))

    efa_supported: EfaSupportedFlag = _dc.field(metadata=_base.field_metadata(
        member_name='EfaSupported',
        shape_name='EfaSupportedFlag',
    ))

    efa_info: EfaInfo = _dc.field(metadata=_base.field_metadata(
        member_name='EfaInfo',
        shape_name='EfaInfo',
    ))

    encryption_in_transit_supported: EncryptionInTransitSupported = _dc.field(metadata=_base.field_metadata(
        member_name='EncryptionInTransitSupported',
        shape_name='EncryptionInTransitSupported',
    ))

    ena_srd_supported: EnaSrdSupported = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdSupported',
        shape_name='EnaSrdSupported',
    ))

    bandwidth_weightings: BandwidthWeightingTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='BandwidthWeightings',
        shape_name='BandwidthWeightingTypeList',
    ))


@_dc.dataclass(frozen=True)
class NetworkInterfaceAttachment(
    _base.Shape,
    shape_name='NetworkInterfaceAttachment',
):
    attach_time: _base.DateTime = _dc.field(metadata=_base.field_metadata(
        member_name='AttachTime',
        shape_name='DateTime',
    ))

    attachment_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AttachmentId',
        shape_name='String',
    ))

    delete_on_termination: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DeleteOnTermination',
        shape_name='Boolean',
    ))

    device_index: int = _dc.field(metadata=_base.field_metadata(
        member_name='DeviceIndex',
        shape_name='Integer',
    ))

    network_card_index: int = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkCardIndex',
        shape_name='Integer',
    ))

    instance_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceId',
        shape_name='String',
    ))

    instance_owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceOwnerId',
        shape_name='String',
    ))

    status: AttachmentStatus = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='AttachmentStatus',
    ))

    ena_srd_specification: AttachmentEnaSrdSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdSpecification',
        shape_name='AttachmentEnaSrdSpecification',
    ))


NetworkInterfacePrivateIpAddressList: _ta.TypeAlias = _ta.Sequence[NetworkInterfacePrivateIpAddress]

NeuronDeviceInfoList: _ta.TypeAlias = _ta.Sequence[NeuronDeviceInfo]

SubnetIpv6CidrBlockAssociationSet: _ta.TypeAlias = _ta.Sequence[SubnetIpv6CidrBlockAssociation]

VpcCidrBlockAssociationSet: _ta.TypeAlias = _ta.Sequence[VpcCidrBlockAssociation]

VpcIpv6CidrBlockAssociationSet: _ta.TypeAlias = _ta.Sequence[VpcIpv6CidrBlockAssociation]


@_dc.dataclass(frozen=True)
class DescribeAddressesRequest(
    _base.Shape,
    shape_name='DescribeAddressesRequest',
):
    public_ips: PublicIpStringList = _dc.field(metadata=_base.field_metadata(
        member_name='PublicIps',
        shape_name='PublicIpStringList',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))

    allocation_ids: AllocationIdList = _dc.field(metadata=_base.field_metadata(
        member_name='AllocationIds',
        shape_name='AllocationIdList',
    ))


@_dc.dataclass(frozen=True)
class DescribeInstanceTypesRequest(
    _base.Shape,
    shape_name='DescribeInstanceTypesRequest',
):
    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    instance_types: RequestInstanceTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceTypes',
        shape_name='RequestInstanceTypeList',
    ))

    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))

    max_results: DITMaxResults = _dc.field(metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DITMaxResults',
    ))

    next_token: NextToken = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='NextToken',
    ))


@_dc.dataclass(frozen=True)
class DescribeInstancesRequest(
    _base.Shape,
    shape_name='DescribeInstancesRequest',
):
    instance_ids: InstanceIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceIds',
        shape_name='InstanceIdStringList',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))

    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: int = _dc.field(metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='Integer',
    ))


@_dc.dataclass(frozen=True)
class DescribeInternetGatewaysRequest(
    _base.Shape,
    shape_name='DescribeInternetGatewaysRequest',
):
    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeInternetGatewaysMaxResults = _dc.field(metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeInternetGatewaysMaxResults',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    internet_gateway_ids: InternetGatewayIdList = _dc.field(metadata=_base.field_metadata(
        member_name='InternetGatewayIds',
        shape_name='InternetGatewayIdList',
    ))

    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True)
class DescribeKeyPairsRequest(
    _base.Shape,
    shape_name='DescribeKeyPairsRequest',
):
    key_names: KeyNameStringList = _dc.field(metadata=_base.field_metadata(
        member_name='KeyNames',
        shape_name='KeyNameStringList',
    ))

    key_pair_ids: KeyPairIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='KeyPairIds',
        shape_name='KeyPairIdStringList',
    ))

    include_public_key: bool = _dc.field(metadata=_base.field_metadata(
        member_name='IncludePublicKey',
        shape_name='Boolean',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True)
class DescribeNetworkInterfacesRequest(
    _base.Shape,
    shape_name='DescribeNetworkInterfacesRequest',
):
    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeNetworkInterfacesMaxResults = _dc.field(metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeNetworkInterfacesMaxResults',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    network_interface_ids: NetworkInterfaceIdList = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaceIds',
        shape_name='NetworkInterfaceIdList',
    ))

    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True)
class DescribeSecurityGroupsRequest(
    _base.Shape,
    shape_name='DescribeSecurityGroupsRequest',
):
    group_ids: GroupIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='GroupIds',
        shape_name='GroupIdStringList',
    ))

    group_names: GroupNameStringList = _dc.field(metadata=_base.field_metadata(
        member_name='GroupNames',
        shape_name='GroupNameStringList',
    ))

    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeSecurityGroupsMaxResults = _dc.field(metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeSecurityGroupsMaxResults',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))


@_dc.dataclass(frozen=True)
class DescribeSubnetsRequest(
    _base.Shape,
    shape_name='DescribeSubnetsRequest',
):
    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))

    subnet_ids: SubnetIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetIds',
        shape_name='SubnetIdStringList',
    ))

    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeSubnetsMaxResults = _dc.field(metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeSubnetsMaxResults',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class DescribeVpcsRequest(
    _base.Shape,
    shape_name='DescribeVpcsRequest',
):
    filters: FilterList = _dc.field(metadata=_base.field_metadata(
        member_name='Filters',
        shape_name='FilterList',
    ))

    vpc_ids: VpcIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='VpcIds',
        shape_name='VpcIdStringList',
    ))

    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    max_results: DescribeVpcsMaxResults = _dc.field(metadata=_base.field_metadata(
        member_name='MaxResults',
        shape_name='DescribeVpcsMaxResults',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class FpgaInfo(
    _base.Shape,
    shape_name='FpgaInfo',
):
    fpgas: FpgaDeviceInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='Fpgas',
        shape_name='FpgaDeviceInfoList',
    ))

    total_fpga_memory_in_mi_b: TotalFpgaMemory = _dc.field(metadata=_base.field_metadata(
        member_name='TotalFpgaMemoryInMiB',
        shape_name='totalFpgaMemory',
    ))


@_dc.dataclass(frozen=True)
class GpuInfo(
    _base.Shape,
    shape_name='GpuInfo',
):
    gpus: GpuDeviceInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='Gpus',
        shape_name='GpuDeviceInfoList',
    ))

    total_gpu_memory_in_mi_b: TotalGpuMemory = _dc.field(metadata=_base.field_metadata(
        member_name='TotalGpuMemoryInMiB',
        shape_name='totalGpuMemory',
    ))


@_dc.dataclass(frozen=True)
class InferenceAcceleratorInfo(
    _base.Shape,
    shape_name='InferenceAcceleratorInfo',
):
    accelerators: InferenceDeviceInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='Accelerators',
        shape_name='InferenceDeviceInfoList',
    ))

    total_inference_memory_in_mi_b: TotalInferenceMemory = _dc.field(metadata=_base.field_metadata(
        member_name='TotalInferenceMemoryInMiB',
        shape_name='totalInferenceMemory',
    ))


InstanceBlockDeviceMappingList: _ta.TypeAlias = _ta.Sequence[InstanceBlockDeviceMapping]


@_dc.dataclass(frozen=True)
class InstanceNetworkInterface(
    _base.Shape,
    shape_name='InstanceNetworkInterface',
):
    association: InstanceNetworkInterfaceAssociation = _dc.field(metadata=_base.field_metadata(
        member_name='Association',
        shape_name='InstanceNetworkInterfaceAssociation',
    ))

    attachment: InstanceNetworkInterfaceAttachment = _dc.field(metadata=_base.field_metadata(
        member_name='Attachment',
        shape_name='InstanceNetworkInterfaceAttachment',
    ))

    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='String',
    ))

    groups: GroupIdentifierList = _dc.field(metadata=_base.field_metadata(
        member_name='Groups',
        shape_name='GroupIdentifierList',
    ))

    ipv6_addresses: InstanceIpv6AddressList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Addresses',
        shape_name='InstanceIpv6AddressList',
    ))

    mac_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='MacAddress',
        shape_name='String',
    ))

    network_interface_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        shape_name='String',
    ))

    owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='OwnerId',
        shape_name='String',
    ))

    private_dns_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        shape_name='String',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))

    private_ip_addresses: InstancePrivateIpAddressList = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddresses',
        shape_name='InstancePrivateIpAddressList',
    ))

    source_dest_check: bool = _dc.field(metadata=_base.field_metadata(
        member_name='SourceDestCheck',
        shape_name='Boolean',
    ))

    status: NetworkInterfaceStatus = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='NetworkInterfaceStatus',
    ))

    subnet_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetId',
        shape_name='String',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))

    interface_type: str = _dc.field(metadata=_base.field_metadata(
        member_name='InterfaceType',
        shape_name='String',
    ))

    ipv4_prefixes: InstanceIpv4PrefixList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv4Prefixes',
        shape_name='InstanceIpv4PrefixList',
    ))

    ipv6_prefixes: InstanceIpv6PrefixList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Prefixes',
        shape_name='InstanceIpv6PrefixList',
    ))

    connection_tracking_configuration: ConnectionTrackingSpecificationResponse = _dc.field(metadata=_base.field_metadata(
        member_name='ConnectionTrackingConfiguration',
        shape_name='ConnectionTrackingSpecificationResponse',
    ))

    operator: OperatorResponse = _dc.field(metadata=_base.field_metadata(
        member_name='Operator',
        shape_name='OperatorResponse',
    ))


InstanceNetworkInterfaceSpecificationList: _ta.TypeAlias = _ta.Sequence[InstanceNetworkInterfaceSpecification]

InternetGatewayList: _ta.TypeAlias = _ta.Sequence[InternetGateway]

IpPermissionList: _ta.TypeAlias = _ta.Sequence[IpPermission]


@_dc.dataclass(frozen=True)
class MediaAcceleratorInfo(
    _base.Shape,
    shape_name='MediaAcceleratorInfo',
):
    accelerators: MediaDeviceInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='Accelerators',
        shape_name='MediaDeviceInfoList',
    ))

    total_media_memory_in_mi_b: TotalMediaMemory = _dc.field(metadata=_base.field_metadata(
        member_name='TotalMediaMemoryInMiB',
        shape_name='TotalMediaMemory',
    ))


@_dc.dataclass(frozen=True)
class NetworkInterface(
    _base.Shape,
    shape_name='NetworkInterface',
):
    association: NetworkInterfaceAssociation = _dc.field(metadata=_base.field_metadata(
        member_name='Association',
        shape_name='NetworkInterfaceAssociation',
    ))

    attachment: NetworkInterfaceAttachment = _dc.field(metadata=_base.field_metadata(
        member_name='Attachment',
        shape_name='NetworkInterfaceAttachment',
    ))

    availability_zone: str = _dc.field(metadata=_base.field_metadata(
        member_name='AvailabilityZone',
        shape_name='String',
    ))

    connection_tracking_configuration: ConnectionTrackingConfiguration = _dc.field(metadata=_base.field_metadata(
        member_name='ConnectionTrackingConfiguration',
        shape_name='ConnectionTrackingConfiguration',
    ))

    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='String',
    ))

    groups: GroupIdentifierList = _dc.field(metadata=_base.field_metadata(
        member_name='Groups',
        shape_name='GroupIdentifierList',
    ))

    interface_type: NetworkInterfaceType = _dc.field(metadata=_base.field_metadata(
        member_name='InterfaceType',
        shape_name='NetworkInterfaceType',
    ))

    ipv6_addresses: NetworkInterfaceIpv6AddressesList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Addresses',
        shape_name='NetworkInterfaceIpv6AddressesList',
    ))

    mac_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='MacAddress',
        shape_name='String',
    ))

    network_interface_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaceId',
        shape_name='String',
    ))

    outpost_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='OutpostArn',
        shape_name='String',
    ))

    owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='OwnerId',
        shape_name='String',
    ))

    private_dns_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        shape_name='String',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))

    private_ip_addresses: NetworkInterfacePrivateIpAddressList = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddresses',
        shape_name='NetworkInterfacePrivateIpAddressList',
    ))

    ipv4_prefixes: Ipv4PrefixesList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv4Prefixes',
        shape_name='Ipv4PrefixesList',
    ))

    ipv6_prefixes: Ipv6PrefixesList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Prefixes',
        shape_name='Ipv6PrefixesList',
    ))

    requester_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='RequesterId',
        shape_name='String',
    ))

    requester_managed: bool = _dc.field(metadata=_base.field_metadata(
        member_name='RequesterManaged',
        shape_name='Boolean',
    ))

    source_dest_check: bool = _dc.field(metadata=_base.field_metadata(
        member_name='SourceDestCheck',
        shape_name='Boolean',
    ))

    status: NetworkInterfaceStatus = _dc.field(metadata=_base.field_metadata(
        member_name='Status',
        shape_name='NetworkInterfaceStatus',
    ))

    subnet_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetId',
        shape_name='String',
    ))

    tag_set: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='TagSet',
        shape_name='TagList',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))

    deny_all_igw_traffic: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DenyAllIgwTraffic',
        shape_name='Boolean',
    ))

    ipv6_native: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Native',
        shape_name='Boolean',
    ))

    ipv6_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Address',
        shape_name='String',
    ))

    operator: OperatorResponse = _dc.field(metadata=_base.field_metadata(
        member_name='Operator',
        shape_name='OperatorResponse',
    ))


@_dc.dataclass(frozen=True)
class NeuronInfo(
    _base.Shape,
    shape_name='NeuronInfo',
):
    neuron_devices: NeuronDeviceInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='NeuronDevices',
        shape_name='NeuronDeviceInfoList',
    ))

    total_neuron_device_memory_in_mi_b: TotalNeuronMemory = _dc.field(metadata=_base.field_metadata(
        member_name='TotalNeuronDeviceMemoryInMiB',
        shape_name='TotalNeuronMemory',
    ))


@_dc.dataclass(frozen=True)
class StartInstancesResult(
    _base.Shape,
    shape_name='StartInstancesResult',
):
    starting_instances: InstanceStateChangeList = _dc.field(metadata=_base.field_metadata(
        member_name='StartingInstances',
        shape_name='InstanceStateChangeList',
    ))


@_dc.dataclass(frozen=True)
class StopInstancesResult(
    _base.Shape,
    shape_name='StopInstancesResult',
):
    stopping_instances: InstanceStateChangeList = _dc.field(metadata=_base.field_metadata(
        member_name='StoppingInstances',
        shape_name='InstanceStateChangeList',
    ))


@_dc.dataclass(frozen=True)
class Subnet(
    _base.Shape,
    shape_name='Subnet',
):
    availability_zone_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='AvailabilityZoneId',
        shape_name='String',
    ))

    enable_lni_at_device_index: int = _dc.field(metadata=_base.field_metadata(
        member_name='EnableLniAtDeviceIndex',
        shape_name='Integer',
    ))

    map_customer_owned_ip_on_launch: bool = _dc.field(metadata=_base.field_metadata(
        member_name='MapCustomerOwnedIpOnLaunch',
        shape_name='Boolean',
    ))

    customer_owned_ipv4_pool: CoipPoolId = _dc.field(metadata=_base.field_metadata(
        member_name='CustomerOwnedIpv4Pool',
        shape_name='CoipPoolId',
    ))

    owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='OwnerId',
        shape_name='String',
    ))

    assign_ipv6_address_on_creation: bool = _dc.field(metadata=_base.field_metadata(
        member_name='AssignIpv6AddressOnCreation',
        shape_name='Boolean',
    ))

    ipv6_cidr_block_association_set: SubnetIpv6CidrBlockAssociationSet = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6CidrBlockAssociationSet',
        shape_name='SubnetIpv6CidrBlockAssociationSet',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))

    subnet_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetArn',
        shape_name='String',
    ))

    outpost_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='OutpostArn',
        shape_name='String',
    ))

    enable_dns64: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnableDns64',
        shape_name='Boolean',
    ))

    ipv6_native: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Native',
        shape_name='Boolean',
    ))

    private_dns_name_options_on_launch: PrivateDnsNameOptionsOnLaunch = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateDnsNameOptionsOnLaunch',
        shape_name='PrivateDnsNameOptionsOnLaunch',
    ))

    block_public_access_states: BlockPublicAccessStates = _dc.field(metadata=_base.field_metadata(
        member_name='BlockPublicAccessStates',
        shape_name='BlockPublicAccessStates',
    ))

    subnet_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetId',
        shape_name='String',
    ))

    state: SubnetState = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='SubnetState',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))

    cidr_block: str = _dc.field(metadata=_base.field_metadata(
        member_name='CidrBlock',
        shape_name='String',
    ))

    available_ip_address_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='AvailableIpAddressCount',
        shape_name='Integer',
    ))

    availability_zone: str = _dc.field(metadata=_base.field_metadata(
        member_name='AvailabilityZone',
        shape_name='String',
    ))

    default_for_az: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DefaultForAz',
        shape_name='Boolean',
    ))

    map_public_ip_on_launch: bool = _dc.field(metadata=_base.field_metadata(
        member_name='MapPublicIpOnLaunch',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class TerminateInstancesResult(
    _base.Shape,
    shape_name='TerminateInstancesResult',
):
    terminating_instances: InstanceStateChangeList = _dc.field(metadata=_base.field_metadata(
        member_name='TerminatingInstances',
        shape_name='InstanceStateChangeList',
    ))


@_dc.dataclass(frozen=True)
class Vpc(
    _base.Shape,
    shape_name='Vpc',
):
    owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='OwnerId',
        shape_name='String',
    ))

    instance_tenancy: Tenancy = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceTenancy',
        shape_name='Tenancy',
    ))

    ipv6_cidr_block_association_set: VpcIpv6CidrBlockAssociationSet = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6CidrBlockAssociationSet',
        shape_name='VpcIpv6CidrBlockAssociationSet',
    ))

    cidr_block_association_set: VpcCidrBlockAssociationSet = _dc.field(metadata=_base.field_metadata(
        member_name='CidrBlockAssociationSet',
        shape_name='VpcCidrBlockAssociationSet',
    ))

    is_default: bool = _dc.field(metadata=_base.field_metadata(
        member_name='IsDefault',
        shape_name='Boolean',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))

    block_public_access_states: BlockPublicAccessStates = _dc.field(metadata=_base.field_metadata(
        member_name='BlockPublicAccessStates',
        shape_name='BlockPublicAccessStates',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))

    state: VpcState = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='VpcState',
    ))

    cidr_block: str = _dc.field(metadata=_base.field_metadata(
        member_name='CidrBlock',
        shape_name='String',
    ))

    dhcp_options_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='DhcpOptionsId',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class DescribeInternetGatewaysResult(
    _base.Shape,
    shape_name='DescribeInternetGatewaysResult',
):
    internet_gateways: InternetGatewayList = _dc.field(metadata=_base.field_metadata(
        member_name='InternetGateways',
        shape_name='InternetGatewayList',
    ))

    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))


InstanceNetworkInterfaceList: _ta.TypeAlias = _ta.Sequence[InstanceNetworkInterface]


@_dc.dataclass(frozen=True)
class InstanceTypeInfo(
    _base.Shape,
    shape_name='InstanceTypeInfo',
):
    instance_type: InstanceType = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceType',
        shape_name='InstanceType',
    ))

    current_generation: CurrentGenerationFlag = _dc.field(metadata=_base.field_metadata(
        member_name='CurrentGeneration',
        shape_name='CurrentGenerationFlag',
    ))

    free_tier_eligible: FreeTierEligibleFlag = _dc.field(metadata=_base.field_metadata(
        member_name='FreeTierEligible',
        shape_name='FreeTierEligibleFlag',
    ))

    supported_usage_classes: UsageClassTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedUsageClasses',
        shape_name='UsageClassTypeList',
    ))

    supported_root_device_types: RootDeviceTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedRootDeviceTypes',
        shape_name='RootDeviceTypeList',
    ))

    supported_virtualization_types: VirtualizationTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedVirtualizationTypes',
        shape_name='VirtualizationTypeList',
    ))

    bare_metal: BareMetalFlag = _dc.field(metadata=_base.field_metadata(
        member_name='BareMetal',
        shape_name='BareMetalFlag',
    ))

    hypervisor: InstanceTypeHypervisor = _dc.field(metadata=_base.field_metadata(
        member_name='Hypervisor',
        shape_name='InstanceTypeHypervisor',
    ))

    processor_info: ProcessorInfo = _dc.field(metadata=_base.field_metadata(
        member_name='ProcessorInfo',
        shape_name='ProcessorInfo',
    ))

    v_cpu_info: VCpuInfo = _dc.field(metadata=_base.field_metadata(
        member_name='VCpuInfo',
        shape_name='VCpuInfo',
    ))

    memory_info: MemoryInfo = _dc.field(metadata=_base.field_metadata(
        member_name='MemoryInfo',
        shape_name='MemoryInfo',
    ))

    instance_storage_supported: InstanceStorageFlag = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceStorageSupported',
        shape_name='InstanceStorageFlag',
    ))

    instance_storage_info: InstanceStorageInfo = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceStorageInfo',
        shape_name='InstanceStorageInfo',
    ))

    ebs_info: EbsInfo = _dc.field(metadata=_base.field_metadata(
        member_name='EbsInfo',
        shape_name='EbsInfo',
    ))

    network_info: NetworkInfo = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInfo',
        shape_name='NetworkInfo',
    ))

    gpu_info: GpuInfo = _dc.field(metadata=_base.field_metadata(
        member_name='GpuInfo',
        shape_name='GpuInfo',
    ))

    fpga_info: FpgaInfo = _dc.field(metadata=_base.field_metadata(
        member_name='FpgaInfo',
        shape_name='FpgaInfo',
    ))

    placement_group_info: PlacementGroupInfo = _dc.field(metadata=_base.field_metadata(
        member_name='PlacementGroupInfo',
        shape_name='PlacementGroupInfo',
    ))

    inference_accelerator_info: InferenceAcceleratorInfo = _dc.field(metadata=_base.field_metadata(
        member_name='InferenceAcceleratorInfo',
        shape_name='InferenceAcceleratorInfo',
    ))

    hibernation_supported: HibernationFlag = _dc.field(metadata=_base.field_metadata(
        member_name='HibernationSupported',
        shape_name='HibernationFlag',
    ))

    burstable_performance_supported: BurstablePerformanceFlag = _dc.field(metadata=_base.field_metadata(
        member_name='BurstablePerformanceSupported',
        shape_name='BurstablePerformanceFlag',
    ))

    dedicated_hosts_supported: DedicatedHostFlag = _dc.field(metadata=_base.field_metadata(
        member_name='DedicatedHostsSupported',
        shape_name='DedicatedHostFlag',
    ))

    auto_recovery_supported: AutoRecoveryFlag = _dc.field(metadata=_base.field_metadata(
        member_name='AutoRecoverySupported',
        shape_name='AutoRecoveryFlag',
    ))

    supported_boot_modes: BootModeTypeList = _dc.field(metadata=_base.field_metadata(
        member_name='SupportedBootModes',
        shape_name='BootModeTypeList',
    ))

    nitro_enclaves_support: NitroEnclavesSupport = _dc.field(metadata=_base.field_metadata(
        member_name='NitroEnclavesSupport',
        shape_name='NitroEnclavesSupport',
    ))

    nitro_tpm_support: NitroTpmSupport = _dc.field(metadata=_base.field_metadata(
        member_name='NitroTpmSupport',
        shape_name='NitroTpmSupport',
    ))

    nitro_tpm_info: NitroTpmInfo = _dc.field(metadata=_base.field_metadata(
        member_name='NitroTpmInfo',
        shape_name='NitroTpmInfo',
    ))

    media_accelerator_info: MediaAcceleratorInfo = _dc.field(metadata=_base.field_metadata(
        member_name='MediaAcceleratorInfo',
        shape_name='MediaAcceleratorInfo',
    ))

    neuron_info: NeuronInfo = _dc.field(metadata=_base.field_metadata(
        member_name='NeuronInfo',
        shape_name='NeuronInfo',
    ))

    phc_support: PhcSupport = _dc.field(metadata=_base.field_metadata(
        member_name='PhcSupport',
        shape_name='PhcSupport',
    ))


NetworkInterfaceList: _ta.TypeAlias = _ta.Sequence[NetworkInterface]


@_dc.dataclass(frozen=True)
class RunInstancesRequest(
    _base.Shape,
    shape_name='RunInstancesRequest',
):
    block_device_mappings: BlockDeviceMappingRequestList = _dc.field(metadata=_base.field_metadata(
        member_name='BlockDeviceMappings',
        shape_name='BlockDeviceMappingRequestList',
    ))

    image_id: ImageId = _dc.field(metadata=_base.field_metadata(
        member_name='ImageId',
        shape_name='ImageId',
    ))

    instance_type: InstanceType = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceType',
        shape_name='InstanceType',
    ))

    ipv6_address_count: int = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6AddressCount',
        shape_name='Integer',
    ))

    ipv6_addresses: InstanceIpv6AddressList = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Addresses',
        shape_name='InstanceIpv6AddressList',
    ))

    kernel_id: KernelId = _dc.field(metadata=_base.field_metadata(
        member_name='KernelId',
        shape_name='KernelId',
    ))

    key_name: KeyPairName = _dc.field(metadata=_base.field_metadata(
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

    monitoring: RunInstancesMonitoringEnabled = _dc.field(metadata=_base.field_metadata(
        member_name='Monitoring',
        shape_name='RunInstancesMonitoringEnabled',
    ))

    placement: Placement = _dc.field(metadata=_base.field_metadata(
        member_name='Placement',
        shape_name='Placement',
    ))

    ramdisk_id: RamdiskId = _dc.field(metadata=_base.field_metadata(
        member_name='RamdiskId',
        shape_name='RamdiskId',
    ))

    security_group_ids: SecurityGroupIdStringList = _dc.field(metadata=_base.field_metadata(
        member_name='SecurityGroupIds',
        shape_name='SecurityGroupIdStringList',
    ))

    security_groups: SecurityGroupStringList = _dc.field(metadata=_base.field_metadata(
        member_name='SecurityGroups',
        shape_name='SecurityGroupStringList',
    ))

    subnet_id: SubnetId = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetId',
        shape_name='SubnetId',
    ))

    user_data: RunInstancesUserData = _dc.field(metadata=_base.field_metadata(
        member_name='UserData',
        shape_name='RunInstancesUserData',
    ))

    elastic_gpu_specification: ElasticGpuSpecifications = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticGpuSpecification',
        shape_name='ElasticGpuSpecifications',
    ))

    elastic_inference_accelerators: ElasticInferenceAccelerators = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticInferenceAccelerators',
        shape_name='ElasticInferenceAccelerators',
    ))

    tag_specifications: TagSpecificationList = _dc.field(metadata=_base.field_metadata(
        member_name='TagSpecifications',
        shape_name='TagSpecificationList',
    ))

    launch_template: LaunchTemplateSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='LaunchTemplate',
        shape_name='LaunchTemplateSpecification',
    ))

    instance_market_options: InstanceMarketOptionsRequest = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceMarketOptions',
        shape_name='InstanceMarketOptionsRequest',
    ))

    credit_specification: CreditSpecificationRequest = _dc.field(metadata=_base.field_metadata(
        member_name='CreditSpecification',
        shape_name='CreditSpecificationRequest',
    ))

    cpu_options: CpuOptionsRequest = _dc.field(metadata=_base.field_metadata(
        member_name='CpuOptions',
        shape_name='CpuOptionsRequest',
    ))

    capacity_reservation_specification: CapacityReservationSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationSpecification',
        shape_name='CapacityReservationSpecification',
    ))

    hibernation_options: HibernationOptionsRequest = _dc.field(metadata=_base.field_metadata(
        member_name='HibernationOptions',
        shape_name='HibernationOptionsRequest',
    ))

    license_specifications: LicenseSpecificationListRequest = _dc.field(metadata=_base.field_metadata(
        member_name='LicenseSpecifications',
        shape_name='LicenseSpecificationListRequest',
    ))

    metadata_options: InstanceMetadataOptionsRequest = _dc.field(metadata=_base.field_metadata(
        member_name='MetadataOptions',
        shape_name='InstanceMetadataOptionsRequest',
    ))

    enclave_options: EnclaveOptionsRequest = _dc.field(metadata=_base.field_metadata(
        member_name='EnclaveOptions',
        shape_name='EnclaveOptionsRequest',
    ))

    private_dns_name_options: PrivateDnsNameOptionsRequest = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateDnsNameOptions',
        shape_name='PrivateDnsNameOptionsRequest',
    ))

    maintenance_options: InstanceMaintenanceOptionsRequest = _dc.field(metadata=_base.field_metadata(
        member_name='MaintenanceOptions',
        shape_name='InstanceMaintenanceOptionsRequest',
    ))

    disable_api_stop: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DisableApiStop',
        shape_name='Boolean',
    ))

    enable_primary_ipv6: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnablePrimaryIpv6',
        shape_name='Boolean',
    ))

    network_performance_options: InstanceNetworkPerformanceOptionsRequest = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkPerformanceOptions',
        shape_name='InstanceNetworkPerformanceOptionsRequest',
    ))

    operator: OperatorRequest = _dc.field(metadata=_base.field_metadata(
        member_name='Operator',
        shape_name='OperatorRequest',
    ))

    dry_run: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DryRun',
        shape_name='Boolean',
    ))

    disable_api_termination: bool = _dc.field(metadata=_base.field_metadata(
        member_name='DisableApiTermination',
        shape_name='Boolean',
    ))

    instance_initiated_shutdown_behavior: ShutdownBehavior = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceInitiatedShutdownBehavior',
        shape_name='ShutdownBehavior',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))

    client_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='ClientToken',
        shape_name='String',
    ))

    additional_info: str = _dc.field(metadata=_base.field_metadata(
        member_name='AdditionalInfo',
        shape_name='String',
    ))

    network_interfaces: InstanceNetworkInterfaceSpecificationList = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaces',
        shape_name='InstanceNetworkInterfaceSpecificationList',
    ))

    iam_instance_profile: IamInstanceProfileSpecification = _dc.field(metadata=_base.field_metadata(
        member_name='IamInstanceProfile',
        shape_name='IamInstanceProfileSpecification',
    ))

    ebs_optimized: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EbsOptimized',
        shape_name='Boolean',
    ))


@_dc.dataclass(frozen=True)
class SecurityGroup(
    _base.Shape,
    shape_name='SecurityGroup',
):
    group_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='GroupId',
        shape_name='String',
    ))

    ip_permissions_egress: IpPermissionList = _dc.field(metadata=_base.field_metadata(
        member_name='IpPermissionsEgress',
        shape_name='IpPermissionList',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))

    security_group_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='SecurityGroupArn',
        shape_name='String',
    ))

    owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='OwnerId',
        shape_name='String',
    ))

    group_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='GroupName',
        shape_name='String',
    ))

    description: str = _dc.field(metadata=_base.field_metadata(
        member_name='Description',
        shape_name='String',
    ))

    ip_permissions: IpPermissionList = _dc.field(metadata=_base.field_metadata(
        member_name='IpPermissions',
        shape_name='IpPermissionList',
    ))


SubnetList: _ta.TypeAlias = _ta.Sequence[Subnet]

VpcList: _ta.TypeAlias = _ta.Sequence[Vpc]


@_dc.dataclass(frozen=True)
class DescribeNetworkInterfacesResult(
    _base.Shape,
    shape_name='DescribeNetworkInterfacesResult',
):
    network_interfaces: NetworkInterfaceList = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaces',
        shape_name='NetworkInterfaceList',
    ))

    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))


@_dc.dataclass(frozen=True)
class DescribeSubnetsResult(
    _base.Shape,
    shape_name='DescribeSubnetsResult',
):
    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    subnets: SubnetList = _dc.field(metadata=_base.field_metadata(
        member_name='Subnets',
        shape_name='SubnetList',
    ))


@_dc.dataclass(frozen=True)
class DescribeVpcsResult(
    _base.Shape,
    shape_name='DescribeVpcsResult',
):
    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    vpcs: VpcList = _dc.field(metadata=_base.field_metadata(
        member_name='Vpcs',
        shape_name='VpcList',
    ))


@_dc.dataclass(frozen=True)
class Instance(
    _base.Shape,
    shape_name='Instance',
):
    architecture: ArchitectureValues = _dc.field(metadata=_base.field_metadata(
        member_name='Architecture',
        shape_name='ArchitectureValues',
    ))

    block_device_mappings: InstanceBlockDeviceMappingList = _dc.field(metadata=_base.field_metadata(
        member_name='BlockDeviceMappings',
        shape_name='InstanceBlockDeviceMappingList',
    ))

    client_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='ClientToken',
        shape_name='String',
    ))

    ebs_optimized: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EbsOptimized',
        shape_name='Boolean',
    ))

    ena_support: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSupport',
        shape_name='Boolean',
    ))

    hypervisor: HypervisorType = _dc.field(metadata=_base.field_metadata(
        member_name='Hypervisor',
        shape_name='HypervisorType',
    ))

    iam_instance_profile: IamInstanceProfile = _dc.field(metadata=_base.field_metadata(
        member_name='IamInstanceProfile',
        shape_name='IamInstanceProfile',
    ))

    instance_lifecycle: InstanceLifecycleType = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceLifecycle',
        shape_name='InstanceLifecycleType',
    ))

    elastic_gpu_associations: ElasticGpuAssociationList = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticGpuAssociations',
        shape_name='ElasticGpuAssociationList',
    ))

    elastic_inference_accelerator_associations: ElasticInferenceAcceleratorAssociationList = _dc.field(metadata=_base.field_metadata(
        member_name='ElasticInferenceAcceleratorAssociations',
        shape_name='ElasticInferenceAcceleratorAssociationList',
    ))

    network_interfaces: InstanceNetworkInterfaceList = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkInterfaces',
        shape_name='InstanceNetworkInterfaceList',
    ))

    outpost_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='OutpostArn',
        shape_name='String',
    ))

    root_device_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='RootDeviceName',
        shape_name='String',
    ))

    root_device_type: DeviceType = _dc.field(metadata=_base.field_metadata(
        member_name='RootDeviceType',
        shape_name='DeviceType',
    ))

    security_groups: GroupIdentifierList = _dc.field(metadata=_base.field_metadata(
        member_name='SecurityGroups',
        shape_name='GroupIdentifierList',
    ))

    source_dest_check: bool = _dc.field(metadata=_base.field_metadata(
        member_name='SourceDestCheck',
        shape_name='Boolean',
    ))

    spot_instance_request_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='SpotInstanceRequestId',
        shape_name='String',
    ))

    sriov_net_support: str = _dc.field(metadata=_base.field_metadata(
        member_name='SriovNetSupport',
        shape_name='String',
    ))

    state_reason: StateReason = _dc.field(metadata=_base.field_metadata(
        member_name='StateReason',
        shape_name='StateReason',
    ))

    tags: _base.TagList = _dc.field(metadata=_base.field_metadata(
        member_name='Tags',
        shape_name='TagList',
    ))

    virtualization_type: VirtualizationType = _dc.field(metadata=_base.field_metadata(
        member_name='VirtualizationType',
        shape_name='VirtualizationType',
    ))

    cpu_options: CpuOptions = _dc.field(metadata=_base.field_metadata(
        member_name='CpuOptions',
        shape_name='CpuOptions',
    ))

    capacity_reservation_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationId',
        shape_name='String',
    ))

    capacity_reservation_specification: CapacityReservationSpecificationResponse = _dc.field(metadata=_base.field_metadata(
        member_name='CapacityReservationSpecification',
        shape_name='CapacityReservationSpecificationResponse',
    ))

    hibernation_options: HibernationOptions = _dc.field(metadata=_base.field_metadata(
        member_name='HibernationOptions',
        shape_name='HibernationOptions',
    ))

    licenses: LicenseList = _dc.field(metadata=_base.field_metadata(
        member_name='Licenses',
        shape_name='LicenseList',
    ))

    metadata_options: InstanceMetadataOptionsResponse = _dc.field(metadata=_base.field_metadata(
        member_name='MetadataOptions',
        shape_name='InstanceMetadataOptionsResponse',
    ))

    enclave_options: EnclaveOptions = _dc.field(metadata=_base.field_metadata(
        member_name='EnclaveOptions',
        shape_name='EnclaveOptions',
    ))

    boot_mode: BootModeValues = _dc.field(metadata=_base.field_metadata(
        member_name='BootMode',
        shape_name='BootModeValues',
    ))

    platform_details: str = _dc.field(metadata=_base.field_metadata(
        member_name='PlatformDetails',
        shape_name='String',
    ))

    usage_operation: str = _dc.field(metadata=_base.field_metadata(
        member_name='UsageOperation',
        shape_name='String',
    ))

    usage_operation_update_time: _base.MillisecondDateTime = _dc.field(metadata=_base.field_metadata(
        member_name='UsageOperationUpdateTime',
        shape_name='MillisecondDateTime',
    ))

    private_dns_name_options: PrivateDnsNameOptionsResponse = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateDnsNameOptions',
        shape_name='PrivateDnsNameOptionsResponse',
    ))

    ipv6_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='Ipv6Address',
        shape_name='String',
    ))

    tpm_support: str = _dc.field(metadata=_base.field_metadata(
        member_name='TpmSupport',
        shape_name='String',
    ))

    maintenance_options: InstanceMaintenanceOptions = _dc.field(metadata=_base.field_metadata(
        member_name='MaintenanceOptions',
        shape_name='InstanceMaintenanceOptions',
    ))

    current_instance_boot_mode: InstanceBootModeValues = _dc.field(metadata=_base.field_metadata(
        member_name='CurrentInstanceBootMode',
        shape_name='InstanceBootModeValues',
    ))

    network_performance_options: InstanceNetworkPerformanceOptions = _dc.field(metadata=_base.field_metadata(
        member_name='NetworkPerformanceOptions',
        shape_name='InstanceNetworkPerformanceOptions',
    ))

    operator: OperatorResponse = _dc.field(metadata=_base.field_metadata(
        member_name='Operator',
        shape_name='OperatorResponse',
    ))

    instance_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceId',
        shape_name='String',
    ))

    image_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='ImageId',
        shape_name='String',
    ))

    state: InstanceState = _dc.field(metadata=_base.field_metadata(
        member_name='State',
        shape_name='InstanceState',
    ))

    private_dns_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateDnsName',
        shape_name='String',
    ))

    public_dns_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicDnsName',
        shape_name='String',
    ))

    state_transition_reason: str = _dc.field(metadata=_base.field_metadata(
        member_name='StateTransitionReason',
        shape_name='String',
    ))

    key_name: str = _dc.field(metadata=_base.field_metadata(
        member_name='KeyName',
        shape_name='String',
    ))

    ami_launch_index: int = _dc.field(metadata=_base.field_metadata(
        member_name='AmiLaunchIndex',
        shape_name='Integer',
    ))

    product_codes: ProductCodeList = _dc.field(metadata=_base.field_metadata(
        member_name='ProductCodes',
        shape_name='ProductCodeList',
    ))

    instance_type: InstanceType = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceType',
        shape_name='InstanceType',
    ))

    launch_time: _base.DateTime = _dc.field(metadata=_base.field_metadata(
        member_name='LaunchTime',
        shape_name='DateTime',
    ))

    placement: Placement = _dc.field(metadata=_base.field_metadata(
        member_name='Placement',
        shape_name='Placement',
    ))

    kernel_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='KernelId',
        shape_name='String',
    ))

    ramdisk_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='RamdiskId',
        shape_name='String',
    ))

    platform: PlatformValues = _dc.field(metadata=_base.field_metadata(
        member_name='Platform',
        shape_name='PlatformValues',
    ))

    monitoring: Monitoring = _dc.field(metadata=_base.field_metadata(
        member_name='Monitoring',
        shape_name='Monitoring',
    ))

    subnet_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='SubnetId',
        shape_name='String',
    ))

    vpc_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='VpcId',
        shape_name='String',
    ))

    private_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PrivateIpAddress',
        shape_name='String',
    ))

    public_ip_address: str = _dc.field(metadata=_base.field_metadata(
        member_name='PublicIpAddress',
        shape_name='String',
    ))


InstanceTypeInfoList: _ta.TypeAlias = _ta.Sequence[InstanceTypeInfo]

SecurityGroupList: _ta.TypeAlias = _ta.Sequence[SecurityGroup]


@_dc.dataclass(frozen=True)
class DescribeInstanceTypesResult(
    _base.Shape,
    shape_name='DescribeInstanceTypesResult',
):
    instance_types: InstanceTypeInfoList = _dc.field(metadata=_base.field_metadata(
        member_name='InstanceTypes',
        shape_name='InstanceTypeInfoList',
    ))

    next_token: NextToken = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='NextToken',
    ))


@_dc.dataclass(frozen=True)
class DescribeSecurityGroupsResult(
    _base.Shape,
    shape_name='DescribeSecurityGroupsResult',
):
    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    security_groups: SecurityGroupList = _dc.field(metadata=_base.field_metadata(
        member_name='SecurityGroups',
        shape_name='SecurityGroupList',
    ))


InstanceList: _ta.TypeAlias = _ta.Sequence[Instance]


@_dc.dataclass(frozen=True)
class Reservation(
    _base.Shape,
    shape_name='Reservation',
):
    reservation_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='ReservationId',
        shape_name='String',
    ))

    owner_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='OwnerId',
        shape_name='String',
    ))

    requester_id: str = _dc.field(metadata=_base.field_metadata(
        member_name='RequesterId',
        shape_name='String',
    ))

    groups: GroupIdentifierList = _dc.field(metadata=_base.field_metadata(
        member_name='Groups',
        shape_name='GroupIdentifierList',
    ))

    instances: InstanceList = _dc.field(metadata=_base.field_metadata(
        member_name='Instances',
        shape_name='InstanceList',
    ))


ReservationList: _ta.TypeAlias = _ta.Sequence[Reservation]


@_dc.dataclass(frozen=True)
class DescribeInstancesResult(
    _base.Shape,
    shape_name='DescribeInstancesResult',
):
    next_token: str = _dc.field(metadata=_base.field_metadata(
        member_name='NextToken',
        shape_name='String',
    ))

    reservations: ReservationList = _dc.field(metadata=_base.field_metadata(
        member_name='Reservations',
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
    CreditSpecificationRequest,
    DescribeAddressesRequest,
    DescribeAddressesResult,
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
    RebootInstancesRequest,
    Reservation,
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
    VpcIpv6CidrBlockAssociation,
])


##


DESCRIBE_ADDRESSES = _base.Operation(
    name='DescribeAddresses',
    input=DescribeAddressesRequest,
    output=DescribeAddressesResult,
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
    DESCRIBE_ADDRESSES,
    DESCRIBE_INSTANCES,
    DESCRIBE_INSTANCE_TYPES,
    DESCRIBE_INTERNET_GATEWAYS,
    DESCRIBE_KEY_PAIRS,
    DESCRIBE_NETWORK_INTERFACES,
    DESCRIBE_SECURITY_GROUPS,
    DESCRIBE_SUBNETS,
    DESCRIBE_VPCS,
    DESCRIBE_VPCS,
    REBOOT_INSTANCES,
    RUN_INSTANCES,
    START_INSTANCES,
    STOP_INSTANCES,
    TERMINATE_INSTANCES,
])
