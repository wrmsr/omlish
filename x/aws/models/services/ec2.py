# flake8: noqa: E501
# fmt: off
import dataclasses as _dc  # noqa
import typing as _ta  # noqa

from .. import base as _base  # noqa


##


AmdSevSnpSpecification = _ta.NewType('AmdSevSnpSpecification', _ta.Literal[
    'enabled',
    'disabled',
])

ArchitectureValues = _ta.NewType('ArchitectureValues', _ta.Literal[
    'i386',
    'x86_64',
    'arm64',
    'x86_64_mac',
    'arm64_mac',
])

AttachmentStatus = _ta.NewType('AttachmentStatus', _ta.Literal[
    'attaching',
    'attached',
    'detaching',
    'detached',
])

BootModeValues = _ta.NewType('BootModeValues', _ta.Literal[
    'legacy-bios',
    'uefi',
    'uefi-preferred',
])

CapacityReservationPreference = _ta.NewType('CapacityReservationPreference', _ta.Literal[
    'capacity-reservations-only',
    'open',
    'none',
])

DeviceType = _ta.NewType('DeviceType', _ta.Literal[
    'ebs',
    'instance-store',
])

ElasticGpuId = _ta.NewType('ElasticGpuId', str)

HostnameType = _ta.NewType('HostnameType', _ta.Literal[
    'ip-name',
    'resource-name',
])

HttpTokensState = _ta.NewType('HttpTokensState', _ta.Literal[
    'optional',
    'required',
])

HypervisorType = _ta.NewType('HypervisorType', _ta.Literal[
    'ovm',
    'xen',
])

InstanceAutoRecoveryState = _ta.NewType('InstanceAutoRecoveryState', _ta.Literal[
    'disabled',
    'default',
])

InstanceBandwidthWeighting = _ta.NewType('InstanceBandwidthWeighting', _ta.Literal[
    'default',
    'vpc-1',
    'ebs-1',
])

InstanceBootModeValues = _ta.NewType('InstanceBootModeValues', _ta.Literal[
    'legacy-bios',
    'uefi',
])

InstanceId = _ta.NewType('InstanceId', str)

InstanceLifecycleType = _ta.NewType('InstanceLifecycleType', _ta.Literal[
    'spot',
    'scheduled',
    'capacity-block',
])

InstanceMetadataEndpointState = _ta.NewType('InstanceMetadataEndpointState', _ta.Literal[
    'disabled',
    'enabled',
])

InstanceMetadataOptionsState = _ta.NewType('InstanceMetadataOptionsState', _ta.Literal[
    'pending',
    'applied',
])

InstanceMetadataProtocolState = _ta.NewType('InstanceMetadataProtocolState', _ta.Literal[
    'disabled',
    'enabled',
])

InstanceMetadataTagsState = _ta.NewType('InstanceMetadataTagsState', _ta.Literal[
    'disabled',
    'enabled',
])

InstanceStateName = _ta.NewType('InstanceStateName', _ta.Literal[
    'pending',
    'running',
    'shutting-down',
    'terminated',
    'stopping',
    'stopped',
])

InstanceType = _ta.NewType('InstanceType', _ta.Literal[
    'a1.medium',
    'a1.large',
    'a1.xlarge',
    'a1.2xlarge',
    'a1.4xlarge',
    'a1.metal',
    'c1.medium',
    'c1.xlarge',
    'c3.large',
    'c3.xlarge',
    'c3.2xlarge',
    'c3.4xlarge',
    'c3.8xlarge',
    'c4.large',
    'c4.xlarge',
    'c4.2xlarge',
    'c4.4xlarge',
    'c4.8xlarge',
    'c5.large',
    'c5.xlarge',
    'c5.2xlarge',
    'c5.4xlarge',
    'c5.9xlarge',
    'c5.12xlarge',
    'c5.18xlarge',
    'c5.24xlarge',
    'c5.metal',
    'c5a.large',
    'c5a.xlarge',
    'c5a.2xlarge',
    'c5a.4xlarge',
    'c5a.8xlarge',
    'c5a.12xlarge',
    'c5a.16xlarge',
    'c5a.24xlarge',
    'c5ad.large',
    'c5ad.xlarge',
    'c5ad.2xlarge',
    'c5ad.4xlarge',
    'c5ad.8xlarge',
    'c5ad.12xlarge',
    'c5ad.16xlarge',
    'c5ad.24xlarge',
    'c5d.large',
    'c5d.xlarge',
    'c5d.2xlarge',
    'c5d.4xlarge',
    'c5d.9xlarge',
    'c5d.12xlarge',
    'c5d.18xlarge',
    'c5d.24xlarge',
    'c5d.metal',
    'c5n.large',
    'c5n.xlarge',
    'c5n.2xlarge',
    'c5n.4xlarge',
    'c5n.9xlarge',
    'c5n.18xlarge',
    'c5n.metal',
    'c6g.medium',
    'c6g.large',
    'c6g.xlarge',
    'c6g.2xlarge',
    'c6g.4xlarge',
    'c6g.8xlarge',
    'c6g.12xlarge',
    'c6g.16xlarge',
    'c6g.metal',
    'c6gd.medium',
    'c6gd.large',
    'c6gd.xlarge',
    'c6gd.2xlarge',
    'c6gd.4xlarge',
    'c6gd.8xlarge',
    'c6gd.12xlarge',
    'c6gd.16xlarge',
    'c6gd.metal',
    'c6gn.medium',
    'c6gn.large',
    'c6gn.xlarge',
    'c6gn.2xlarge',
    'c6gn.4xlarge',
    'c6gn.8xlarge',
    'c6gn.12xlarge',
    'c6gn.16xlarge',
    'c6i.large',
    'c6i.xlarge',
    'c6i.2xlarge',
    'c6i.4xlarge',
    'c6i.8xlarge',
    'c6i.12xlarge',
    'c6i.16xlarge',
    'c6i.24xlarge',
    'c6i.32xlarge',
    'c6i.metal',
    'cc1.4xlarge',
    'cc2.8xlarge',
    'cg1.4xlarge',
    'cr1.8xlarge',
    'd2.xlarge',
    'd2.2xlarge',
    'd2.4xlarge',
    'd2.8xlarge',
    'd3.xlarge',
    'd3.2xlarge',
    'd3.4xlarge',
    'd3.8xlarge',
    'd3en.xlarge',
    'd3en.2xlarge',
    'd3en.4xlarge',
    'd3en.6xlarge',
    'd3en.8xlarge',
    'd3en.12xlarge',
    'dl1.24xlarge',
    'f1.2xlarge',
    'f1.4xlarge',
    'f1.16xlarge',
    'g2.2xlarge',
    'g2.8xlarge',
    'g3.4xlarge',
    'g3.8xlarge',
    'g3.16xlarge',
    'g3s.xlarge',
    'g4ad.xlarge',
    'g4ad.2xlarge',
    'g4ad.4xlarge',
    'g4ad.8xlarge',
    'g4ad.16xlarge',
    'g4dn.xlarge',
    'g4dn.2xlarge',
    'g4dn.4xlarge',
    'g4dn.8xlarge',
    'g4dn.12xlarge',
    'g4dn.16xlarge',
    'g4dn.metal',
    'g5.xlarge',
    'g5.2xlarge',
    'g5.4xlarge',
    'g5.8xlarge',
    'g5.12xlarge',
    'g5.16xlarge',
    'g5.24xlarge',
    'g5.48xlarge',
    'g5g.xlarge',
    'g5g.2xlarge',
    'g5g.4xlarge',
    'g5g.8xlarge',
    'g5g.16xlarge',
    'g5g.metal',
    'hi1.4xlarge',
    'hpc6a.48xlarge',
    'hs1.8xlarge',
    'h1.2xlarge',
    'h1.4xlarge',
    'h1.8xlarge',
    'h1.16xlarge',
    'i2.xlarge',
    'i2.2xlarge',
    'i2.4xlarge',
    'i2.8xlarge',
    'i3.large',
    'i3.xlarge',
    'i3.2xlarge',
    'i3.4xlarge',
    'i3.8xlarge',
    'i3.16xlarge',
    'i3.metal',
    'i3en.large',
    'i3en.xlarge',
    'i3en.2xlarge',
    'i3en.3xlarge',
    'i3en.6xlarge',
    'i3en.12xlarge',
    'i3en.24xlarge',
    'i3en.metal',
    'im4gn.large',
    'im4gn.xlarge',
    'im4gn.2xlarge',
    'im4gn.4xlarge',
    'im4gn.8xlarge',
    'im4gn.16xlarge',
    'inf1.xlarge',
    'inf1.2xlarge',
    'inf1.6xlarge',
    'inf1.24xlarge',
    'is4gen.medium',
    'is4gen.large',
    'is4gen.xlarge',
    'is4gen.2xlarge',
    'is4gen.4xlarge',
    'is4gen.8xlarge',
    'm1.small',
    'm1.medium',
    'm1.large',
    'm1.xlarge',
    'm2.xlarge',
    'm2.2xlarge',
    'm2.4xlarge',
    'm3.medium',
    'm3.large',
    'm3.xlarge',
    'm3.2xlarge',
    'm4.large',
    'm4.xlarge',
    'm4.2xlarge',
    'm4.4xlarge',
    'm4.10xlarge',
    'm4.16xlarge',
    'm5.large',
    'm5.xlarge',
    'm5.2xlarge',
    'm5.4xlarge',
    'm5.8xlarge',
    'm5.12xlarge',
    'm5.16xlarge',
    'm5.24xlarge',
    'm5.metal',
    'm5a.large',
    'm5a.xlarge',
    'm5a.2xlarge',
    'm5a.4xlarge',
    'm5a.8xlarge',
    'm5a.12xlarge',
    'm5a.16xlarge',
    'm5a.24xlarge',
    'm5ad.large',
    'm5ad.xlarge',
    'm5ad.2xlarge',
    'm5ad.4xlarge',
    'm5ad.8xlarge',
    'm5ad.12xlarge',
    'm5ad.16xlarge',
    'm5ad.24xlarge',
    'm5d.large',
    'm5d.xlarge',
    'm5d.2xlarge',
    'm5d.4xlarge',
    'm5d.8xlarge',
    'm5d.12xlarge',
    'm5d.16xlarge',
    'm5d.24xlarge',
    'm5d.metal',
    'm5dn.large',
    'm5dn.xlarge',
    'm5dn.2xlarge',
    'm5dn.4xlarge',
    'm5dn.8xlarge',
    'm5dn.12xlarge',
    'm5dn.16xlarge',
    'm5dn.24xlarge',
    'm5dn.metal',
    'm5n.large',
    'm5n.xlarge',
    'm5n.2xlarge',
    'm5n.4xlarge',
    'm5n.8xlarge',
    'm5n.12xlarge',
    'm5n.16xlarge',
    'm5n.24xlarge',
    'm5n.metal',
    'm5zn.large',
    'm5zn.xlarge',
    'm5zn.2xlarge',
    'm5zn.3xlarge',
    'm5zn.6xlarge',
    'm5zn.12xlarge',
    'm5zn.metal',
    'm6a.large',
    'm6a.xlarge',
    'm6a.2xlarge',
    'm6a.4xlarge',
    'm6a.8xlarge',
    'm6a.12xlarge',
    'm6a.16xlarge',
    'm6a.24xlarge',
    'm6a.32xlarge',
    'm6a.48xlarge',
    'm6g.metal',
    'm6g.medium',
    'm6g.large',
    'm6g.xlarge',
    'm6g.2xlarge',
    'm6g.4xlarge',
    'm6g.8xlarge',
    'm6g.12xlarge',
    'm6g.16xlarge',
    'm6gd.metal',
    'm6gd.medium',
    'm6gd.large',
    'm6gd.xlarge',
    'm6gd.2xlarge',
    'm6gd.4xlarge',
    'm6gd.8xlarge',
    'm6gd.12xlarge',
    'm6gd.16xlarge',
    'm6i.large',
    'm6i.xlarge',
    'm6i.2xlarge',
    'm6i.4xlarge',
    'm6i.8xlarge',
    'm6i.12xlarge',
    'm6i.16xlarge',
    'm6i.24xlarge',
    'm6i.32xlarge',
    'm6i.metal',
    'mac1.metal',
    'p2.xlarge',
    'p2.8xlarge',
    'p2.16xlarge',
    'p3.2xlarge',
    'p3.8xlarge',
    'p3.16xlarge',
    'p3dn.24xlarge',
    'p4d.24xlarge',
    'r3.large',
    'r3.xlarge',
    'r3.2xlarge',
    'r3.4xlarge',
    'r3.8xlarge',
    'r4.large',
    'r4.xlarge',
    'r4.2xlarge',
    'r4.4xlarge',
    'r4.8xlarge',
    'r4.16xlarge',
    'r5.large',
    'r5.xlarge',
    'r5.2xlarge',
    'r5.4xlarge',
    'r5.8xlarge',
    'r5.12xlarge',
    'r5.16xlarge',
    'r5.24xlarge',
    'r5.metal',
    'r5a.large',
    'r5a.xlarge',
    'r5a.2xlarge',
    'r5a.4xlarge',
    'r5a.8xlarge',
    'r5a.12xlarge',
    'r5a.16xlarge',
    'r5a.24xlarge',
    'r5ad.large',
    'r5ad.xlarge',
    'r5ad.2xlarge',
    'r5ad.4xlarge',
    'r5ad.8xlarge',
    'r5ad.12xlarge',
    'r5ad.16xlarge',
    'r5ad.24xlarge',
    'r5b.large',
    'r5b.xlarge',
    'r5b.2xlarge',
    'r5b.4xlarge',
    'r5b.8xlarge',
    'r5b.12xlarge',
    'r5b.16xlarge',
    'r5b.24xlarge',
    'r5b.metal',
    'r5d.large',
    'r5d.xlarge',
    'r5d.2xlarge',
    'r5d.4xlarge',
    'r5d.8xlarge',
    'r5d.12xlarge',
    'r5d.16xlarge',
    'r5d.24xlarge',
    'r5d.metal',
    'r5dn.large',
    'r5dn.xlarge',
    'r5dn.2xlarge',
    'r5dn.4xlarge',
    'r5dn.8xlarge',
    'r5dn.12xlarge',
    'r5dn.16xlarge',
    'r5dn.24xlarge',
    'r5dn.metal',
    'r5n.large',
    'r5n.xlarge',
    'r5n.2xlarge',
    'r5n.4xlarge',
    'r5n.8xlarge',
    'r5n.12xlarge',
    'r5n.16xlarge',
    'r5n.24xlarge',
    'r5n.metal',
    'r6g.medium',
    'r6g.large',
    'r6g.xlarge',
    'r6g.2xlarge',
    'r6g.4xlarge',
    'r6g.8xlarge',
    'r6g.12xlarge',
    'r6g.16xlarge',
    'r6g.metal',
    'r6gd.medium',
    'r6gd.large',
    'r6gd.xlarge',
    'r6gd.2xlarge',
    'r6gd.4xlarge',
    'r6gd.8xlarge',
    'r6gd.12xlarge',
    'r6gd.16xlarge',
    'r6gd.metal',
    'r6i.large',
    'r6i.xlarge',
    'r6i.2xlarge',
    'r6i.4xlarge',
    'r6i.8xlarge',
    'r6i.12xlarge',
    'r6i.16xlarge',
    'r6i.24xlarge',
    'r6i.32xlarge',
    'r6i.metal',
    't1.micro',
    't2.nano',
    't2.micro',
    't2.small',
    't2.medium',
    't2.large',
    't2.xlarge',
    't2.2xlarge',
    't3.nano',
    't3.micro',
    't3.small',
    't3.medium',
    't3.large',
    't3.xlarge',
    't3.2xlarge',
    't3a.nano',
    't3a.micro',
    't3a.small',
    't3a.medium',
    't3a.large',
    't3a.xlarge',
    't3a.2xlarge',
    't4g.nano',
    't4g.micro',
    't4g.small',
    't4g.medium',
    't4g.large',
    't4g.xlarge',
    't4g.2xlarge',
    'u-6tb1.56xlarge',
    'u-6tb1.112xlarge',
    'u-9tb1.112xlarge',
    'u-12tb1.112xlarge',
    'u-6tb1.metal',
    'u-9tb1.metal',
    'u-12tb1.metal',
    'u-18tb1.metal',
    'u-24tb1.metal',
    'vt1.3xlarge',
    'vt1.6xlarge',
    'vt1.24xlarge',
    'x1.16xlarge',
    'x1.32xlarge',
    'x1e.xlarge',
    'x1e.2xlarge',
    'x1e.4xlarge',
    'x1e.8xlarge',
    'x1e.16xlarge',
    'x1e.32xlarge',
    'x2iezn.2xlarge',
    'x2iezn.4xlarge',
    'x2iezn.6xlarge',
    'x2iezn.8xlarge',
    'x2iezn.12xlarge',
    'x2iezn.metal',
    'x2gd.medium',
    'x2gd.large',
    'x2gd.xlarge',
    'x2gd.2xlarge',
    'x2gd.4xlarge',
    'x2gd.8xlarge',
    'x2gd.12xlarge',
    'x2gd.16xlarge',
    'x2gd.metal',
    'z1d.large',
    'z1d.xlarge',
    'z1d.2xlarge',
    'z1d.3xlarge',
    'z1d.6xlarge',
    'z1d.12xlarge',
    'z1d.metal',
    'x2idn.16xlarge',
    'x2idn.24xlarge',
    'x2idn.32xlarge',
    'x2iedn.xlarge',
    'x2iedn.2xlarge',
    'x2iedn.4xlarge',
    'x2iedn.8xlarge',
    'x2iedn.16xlarge',
    'x2iedn.24xlarge',
    'x2iedn.32xlarge',
    'c6a.large',
    'c6a.xlarge',
    'c6a.2xlarge',
    'c6a.4xlarge',
    'c6a.8xlarge',
    'c6a.12xlarge',
    'c6a.16xlarge',
    'c6a.24xlarge',
    'c6a.32xlarge',
    'c6a.48xlarge',
    'c6a.metal',
    'm6a.metal',
    'i4i.large',
    'i4i.xlarge',
    'i4i.2xlarge',
    'i4i.4xlarge',
    'i4i.8xlarge',
    'i4i.16xlarge',
    'i4i.32xlarge',
    'i4i.metal',
    'x2idn.metal',
    'x2iedn.metal',
    'c7g.medium',
    'c7g.large',
    'c7g.xlarge',
    'c7g.2xlarge',
    'c7g.4xlarge',
    'c7g.8xlarge',
    'c7g.12xlarge',
    'c7g.16xlarge',
    'mac2.metal',
    'c6id.large',
    'c6id.xlarge',
    'c6id.2xlarge',
    'c6id.4xlarge',
    'c6id.8xlarge',
    'c6id.12xlarge',
    'c6id.16xlarge',
    'c6id.24xlarge',
    'c6id.32xlarge',
    'c6id.metal',
    'm6id.large',
    'm6id.xlarge',
    'm6id.2xlarge',
    'm6id.4xlarge',
    'm6id.8xlarge',
    'm6id.12xlarge',
    'm6id.16xlarge',
    'm6id.24xlarge',
    'm6id.32xlarge',
    'm6id.metal',
    'r6id.large',
    'r6id.xlarge',
    'r6id.2xlarge',
    'r6id.4xlarge',
    'r6id.8xlarge',
    'r6id.12xlarge',
    'r6id.16xlarge',
    'r6id.24xlarge',
    'r6id.32xlarge',
    'r6id.metal',
    'r6a.large',
    'r6a.xlarge',
    'r6a.2xlarge',
    'r6a.4xlarge',
    'r6a.8xlarge',
    'r6a.12xlarge',
    'r6a.16xlarge',
    'r6a.24xlarge',
    'r6a.32xlarge',
    'r6a.48xlarge',
    'r6a.metal',
    'p4de.24xlarge',
    'u-3tb1.56xlarge',
    'u-18tb1.112xlarge',
    'u-24tb1.112xlarge',
    'trn1.2xlarge',
    'trn1.32xlarge',
    'hpc6id.32xlarge',
    'c6in.large',
    'c6in.xlarge',
    'c6in.2xlarge',
    'c6in.4xlarge',
    'c6in.8xlarge',
    'c6in.12xlarge',
    'c6in.16xlarge',
    'c6in.24xlarge',
    'c6in.32xlarge',
    'm6in.large',
    'm6in.xlarge',
    'm6in.2xlarge',
    'm6in.4xlarge',
    'm6in.8xlarge',
    'm6in.12xlarge',
    'm6in.16xlarge',
    'm6in.24xlarge',
    'm6in.32xlarge',
    'm6idn.large',
    'm6idn.xlarge',
    'm6idn.2xlarge',
    'm6idn.4xlarge',
    'm6idn.8xlarge',
    'm6idn.12xlarge',
    'm6idn.16xlarge',
    'm6idn.24xlarge',
    'm6idn.32xlarge',
    'r6in.large',
    'r6in.xlarge',
    'r6in.2xlarge',
    'r6in.4xlarge',
    'r6in.8xlarge',
    'r6in.12xlarge',
    'r6in.16xlarge',
    'r6in.24xlarge',
    'r6in.32xlarge',
    'r6idn.large',
    'r6idn.xlarge',
    'r6idn.2xlarge',
    'r6idn.4xlarge',
    'r6idn.8xlarge',
    'r6idn.12xlarge',
    'r6idn.16xlarge',
    'r6idn.24xlarge',
    'r6idn.32xlarge',
    'c7g.metal',
    'm7g.medium',
    'm7g.large',
    'm7g.xlarge',
    'm7g.2xlarge',
    'm7g.4xlarge',
    'm7g.8xlarge',
    'm7g.12xlarge',
    'm7g.16xlarge',
    'm7g.metal',
    'r7g.medium',
    'r7g.large',
    'r7g.xlarge',
    'r7g.2xlarge',
    'r7g.4xlarge',
    'r7g.8xlarge',
    'r7g.12xlarge',
    'r7g.16xlarge',
    'r7g.metal',
    'c6in.metal',
    'm6in.metal',
    'm6idn.metal',
    'r6in.metal',
    'r6idn.metal',
    'inf2.xlarge',
    'inf2.8xlarge',
    'inf2.24xlarge',
    'inf2.48xlarge',
    'trn1n.32xlarge',
    'i4g.large',
    'i4g.xlarge',
    'i4g.2xlarge',
    'i4g.4xlarge',
    'i4g.8xlarge',
    'i4g.16xlarge',
    'hpc7g.4xlarge',
    'hpc7g.8xlarge',
    'hpc7g.16xlarge',
    'c7gn.medium',
    'c7gn.large',
    'c7gn.xlarge',
    'c7gn.2xlarge',
    'c7gn.4xlarge',
    'c7gn.8xlarge',
    'c7gn.12xlarge',
    'c7gn.16xlarge',
    'p5.48xlarge',
    'm7i.large',
    'm7i.xlarge',
    'm7i.2xlarge',
    'm7i.4xlarge',
    'm7i.8xlarge',
    'm7i.12xlarge',
    'm7i.16xlarge',
    'm7i.24xlarge',
    'm7i.48xlarge',
    'm7i-flex.large',
    'm7i-flex.xlarge',
    'm7i-flex.2xlarge',
    'm7i-flex.4xlarge',
    'm7i-flex.8xlarge',
    'm7a.medium',
    'm7a.large',
    'm7a.xlarge',
    'm7a.2xlarge',
    'm7a.4xlarge',
    'm7a.8xlarge',
    'm7a.12xlarge',
    'm7a.16xlarge',
    'm7a.24xlarge',
    'm7a.32xlarge',
    'm7a.48xlarge',
    'm7a.metal-48xl',
    'hpc7a.12xlarge',
    'hpc7a.24xlarge',
    'hpc7a.48xlarge',
    'hpc7a.96xlarge',
    'c7gd.medium',
    'c7gd.large',
    'c7gd.xlarge',
    'c7gd.2xlarge',
    'c7gd.4xlarge',
    'c7gd.8xlarge',
    'c7gd.12xlarge',
    'c7gd.16xlarge',
    'm7gd.medium',
    'm7gd.large',
    'm7gd.xlarge',
    'm7gd.2xlarge',
    'm7gd.4xlarge',
    'm7gd.8xlarge',
    'm7gd.12xlarge',
    'm7gd.16xlarge',
    'r7gd.medium',
    'r7gd.large',
    'r7gd.xlarge',
    'r7gd.2xlarge',
    'r7gd.4xlarge',
    'r7gd.8xlarge',
    'r7gd.12xlarge',
    'r7gd.16xlarge',
    'r7a.medium',
    'r7a.large',
    'r7a.xlarge',
    'r7a.2xlarge',
    'r7a.4xlarge',
    'r7a.8xlarge',
    'r7a.12xlarge',
    'r7a.16xlarge',
    'r7a.24xlarge',
    'r7a.32xlarge',
    'r7a.48xlarge',
    'c7i.large',
    'c7i.xlarge',
    'c7i.2xlarge',
    'c7i.4xlarge',
    'c7i.8xlarge',
    'c7i.12xlarge',
    'c7i.16xlarge',
    'c7i.24xlarge',
    'c7i.48xlarge',
    'mac2-m2pro.metal',
    'r7iz.large',
    'r7iz.xlarge',
    'r7iz.2xlarge',
    'r7iz.4xlarge',
    'r7iz.8xlarge',
    'r7iz.12xlarge',
    'r7iz.16xlarge',
    'r7iz.32xlarge',
    'c7a.medium',
    'c7a.large',
    'c7a.xlarge',
    'c7a.2xlarge',
    'c7a.4xlarge',
    'c7a.8xlarge',
    'c7a.12xlarge',
    'c7a.16xlarge',
    'c7a.24xlarge',
    'c7a.32xlarge',
    'c7a.48xlarge',
    'c7a.metal-48xl',
    'r7a.metal-48xl',
    'r7i.large',
    'r7i.xlarge',
    'r7i.2xlarge',
    'r7i.4xlarge',
    'r7i.8xlarge',
    'r7i.12xlarge',
    'r7i.16xlarge',
    'r7i.24xlarge',
    'r7i.48xlarge',
    'dl2q.24xlarge',
    'mac2-m2.metal',
    'i4i.12xlarge',
    'i4i.24xlarge',
    'c7i.metal-24xl',
    'c7i.metal-48xl',
    'm7i.metal-24xl',
    'm7i.metal-48xl',
    'r7i.metal-24xl',
    'r7i.metal-48xl',
    'r7iz.metal-16xl',
    'r7iz.metal-32xl',
    'c7gd.metal',
    'm7gd.metal',
    'r7gd.metal',
    'g6.xlarge',
    'g6.2xlarge',
    'g6.4xlarge',
    'g6.8xlarge',
    'g6.12xlarge',
    'g6.16xlarge',
    'g6.24xlarge',
    'g6.48xlarge',
    'gr6.4xlarge',
    'gr6.8xlarge',
    'c7i-flex.large',
    'c7i-flex.xlarge',
    'c7i-flex.2xlarge',
    'c7i-flex.4xlarge',
    'c7i-flex.8xlarge',
    'u7i-12tb.224xlarge',
    'u7in-16tb.224xlarge',
    'u7in-24tb.224xlarge',
    'u7in-32tb.224xlarge',
    'u7ib-12tb.224xlarge',
    'c7gn.metal',
    'r8g.medium',
    'r8g.large',
    'r8g.xlarge',
    'r8g.2xlarge',
    'r8g.4xlarge',
    'r8g.8xlarge',
    'r8g.12xlarge',
    'r8g.16xlarge',
    'r8g.24xlarge',
    'r8g.48xlarge',
    'r8g.metal-24xl',
    'r8g.metal-48xl',
    'mac2-m1ultra.metal',
    'g6e.xlarge',
    'g6e.2xlarge',
    'g6e.4xlarge',
    'g6e.8xlarge',
    'g6e.12xlarge',
    'g6e.16xlarge',
    'g6e.24xlarge',
    'g6e.48xlarge',
    'c8g.medium',
    'c8g.large',
    'c8g.xlarge',
    'c8g.2xlarge',
    'c8g.4xlarge',
    'c8g.8xlarge',
    'c8g.12xlarge',
    'c8g.16xlarge',
    'c8g.24xlarge',
    'c8g.48xlarge',
    'c8g.metal-24xl',
    'c8g.metal-48xl',
    'm8g.medium',
    'm8g.large',
    'm8g.xlarge',
    'm8g.2xlarge',
    'm8g.4xlarge',
    'm8g.8xlarge',
    'm8g.12xlarge',
    'm8g.16xlarge',
    'm8g.24xlarge',
    'm8g.48xlarge',
    'm8g.metal-24xl',
    'm8g.metal-48xl',
    'x8g.medium',
    'x8g.large',
    'x8g.xlarge',
    'x8g.2xlarge',
    'x8g.4xlarge',
    'x8g.8xlarge',
    'x8g.12xlarge',
    'x8g.16xlarge',
    'x8g.24xlarge',
    'x8g.48xlarge',
    'x8g.metal-24xl',
    'x8g.metal-48xl',
    'i7ie.large',
    'i7ie.xlarge',
    'i7ie.2xlarge',
    'i7ie.3xlarge',
    'i7ie.6xlarge',
    'i7ie.12xlarge',
    'i7ie.18xlarge',
    'i7ie.24xlarge',
    'i7ie.48xlarge',
    'i8g.large',
    'i8g.xlarge',
    'i8g.2xlarge',
    'i8g.4xlarge',
    'i8g.8xlarge',
    'i8g.12xlarge',
    'i8g.16xlarge',
    'i8g.24xlarge',
    'i8g.metal-24xl',
])

MonitoringState = _ta.NewType('MonitoringState', _ta.Literal[
    'disabled',
    'disabling',
    'enabled',
    'pending',
])

NetworkInterfaceStatus = _ta.NewType('NetworkInterfaceStatus', _ta.Literal[
    'available',
    'associated',
    'attaching',
    'in-use',
    'detaching',
])

PlacementGroupId = _ta.NewType('PlacementGroupId', str)

PlacementGroupName = _ta.NewType('PlacementGroupName', str)

PlatformValues = _ta.NewType('PlatformValues', _ta.Literal[
    'Windows',
])

ProductCodeValues = _ta.NewType('ProductCodeValues', _ta.Literal[
    'devpay',
    'marketplace',
])

Tenancy = _ta.NewType('Tenancy', _ta.Literal[
    'default',
    'dedicated',
    'host',
])

VirtualizationType = _ta.NewType('VirtualizationType', _ta.Literal[
    'hvm',
    'paravirtual',
])


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
class EnclaveOptions(
    _base.Shape,
    shape_name='EnclaveOptions',
):
    enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='Enabled',
        shape_name='Boolean',
    ))


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
class InstanceAttachmentEnaSrdUdpSpecification(
    _base.Shape,
    shape_name='InstanceAttachmentEnaSrdUdpSpecification',
):
    ena_srd_udp_enabled: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnaSrdUdpEnabled',
        shape_name='Boolean',
    ))


InstanceIdStringList = _ta.NewType('InstanceIdStringList', _ta.Sequence[InstanceId])


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
class LicenseConfiguration(
    _base.Shape,
    shape_name='LicenseConfiguration',
):
    license_configuration_arn: str = _dc.field(metadata=_base.field_metadata(
        member_name='LicenseConfigurationArn',
        shape_name='String',
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
    enable_resource_name_dns_a_a_a_a_record: bool = _dc.field(metadata=_base.field_metadata(
        member_name='EnableResourceNameDnsAAAARecord',
        shape_name='Boolean',
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


ValueStringList = _ta.NewType('ValueStringList', _ta.Sequence[str])


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


ElasticGpuAssociationList = _ta.NewType('ElasticGpuAssociationList', _ta.Sequence[ElasticGpuAssociation])

ElasticInferenceAcceleratorAssociationList = _ta.NewType('ElasticInferenceAcceleratorAssociationList', _ta.Sequence[ElasticInferenceAcceleratorAssociation])


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


GroupIdentifierList = _ta.NewType('GroupIdentifierList', _ta.Sequence[GroupIdentifier])


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


InstanceIpv4PrefixList = _ta.NewType('InstanceIpv4PrefixList', _ta.Sequence[InstanceIpv4Prefix])

InstanceIpv6AddressList = _ta.NewType('InstanceIpv6AddressList', _ta.Sequence[InstanceIpv6Address])

InstanceIpv6PrefixList = _ta.NewType('InstanceIpv6PrefixList', _ta.Sequence[InstanceIpv6Prefix])


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


LicenseList = _ta.NewType('LicenseList', _ta.Sequence[LicenseConfiguration])

ProductCodeList = _ta.NewType('ProductCodeList', _ta.Sequence[ProductCode])


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


FilterList = _ta.NewType('FilterList', _ta.Sequence[Filter])


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


InstancePrivateIpAddressList = _ta.NewType('InstancePrivateIpAddressList', _ta.Sequence[InstancePrivateIpAddress])

InstanceStateChangeList = _ta.NewType('InstanceStateChangeList', _ta.Sequence[InstanceStateChange])


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


InstanceBlockDeviceMappingList = _ta.NewType('InstanceBlockDeviceMappingList', _ta.Sequence[InstanceBlockDeviceMapping])


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


InstanceNetworkInterfaceList = _ta.NewType('InstanceNetworkInterfaceList', _ta.Sequence[InstanceNetworkInterface])


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


InstanceList = _ta.NewType('InstanceList', _ta.Sequence[Instance])


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


ReservationList = _ta.NewType('ReservationList', _ta.Sequence[Reservation])


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
    CapacityReservationTargetResponse,
    ConnectionTrackingSpecificationResponse,
    CpuOptions,
    ElasticGpuAssociation,
    ElasticInferenceAcceleratorAssociation,
    EnclaveOptions,
    GroupIdentifier,
    HibernationOptions,
    IamInstanceProfile,
    InstanceAttachmentEnaSrdUdpSpecification,
    InstanceIpv4Prefix,
    InstanceIpv6Address,
    InstanceIpv6Prefix,
    InstanceMaintenanceOptions,
    InstanceMetadataOptionsResponse,
    InstanceNetworkInterfaceAssociation,
    InstanceNetworkPerformanceOptions,
    InstanceState,
    LicenseConfiguration,
    Monitoring,
    OperatorResponse,
    Placement,
    PrivateDnsNameOptionsResponse,
    ProductCode,
    StateReason,
    CapacityReservationSpecificationResponse,
    EbsInstanceBlockDevice,
    Filter,
    InstanceAttachmentEnaSrdSpecification,
    InstancePrivateIpAddress,
    InstanceStateChange,
    StartInstancesRequest,
    StopInstancesRequest,
    InstanceBlockDeviceMapping,
    InstanceNetworkInterfaceAttachment,
    DescribeInstancesRequest,
    InstanceNetworkInterface,
    StartInstancesResult,
    StopInstancesResult,
    Instance,
    Reservation,
    DescribeInstancesResult,
])


##


DESCRIBE_INSTANCES = _base.Operation(
    name='DescribeInstances',
    input=DescribeInstancesRequest,
    output=DescribeInstancesResult,
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


ALL_OPERATIONS: frozenset[_base.Operation] = frozenset([
    DESCRIBE_INSTANCES,
    START_INSTANCES,
    STOP_INSTANCES,
])
