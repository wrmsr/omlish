import datetime
import enum
import typing as ta

from omlish import dataclasses as dc


Boolean = ta.Optional[bool]
DateTime = ta.Optional[datetime.datetime]
Float = ta.Optional[float]
Int = ta.Optional[int]
String = ta.Optional[str]

Port = Int


@dc.dataclass(frozen=True)
class Pod:
    lowestBidPriceToResume: Float
    aiApiId: String
    apiKey: String
    consumerUserId: String
    containerDiskInGb: Int
    containerRegistryAuthId: String
    costMultiplier: Float
    costPerHr: float
    adjustedCostPerHr: float
    desiredStatus: 'PodStatus'
    dockerArgs: String
    dockerId: String
    env: list[String]
    gpuCount: int
    gpuPowerLimitPercent: int
    gpus: list['Gpu']
    id: str
    imageName: str
    lastStatusChange: String
    locked: Boolean
    machineId: str
    memoryInGb: float
    name: str
    podType: 'PodType'
    port: Port
    ports: String
    registry: 'PodRegistry'
    templateId: String
    uptimeSeconds: Int
    vcpuCount: float
    version: Int
    volumeEncrypted: bool
    volumeInGb: Float
    volumeKey: String
    volumeMountPath: String
    runtime: 'PodRuntime'
    machine: 'PodMachineInfo'
    latestTelemetry: 'PodTelemetry'
    # endpoint: Endpoint
    # networkVolume: NetworkVolume
    # savingsPlans: [SavingsPlan]


class PodStatus(enum.Enum):
    CREATED = enum.auto()
    RUNNING = enum.auto()
    RESTARTING = enum.auto()
    EXITED = enum.auto()
    PAUSED = enum.auto()
    DEAD = enum.auto()
    TERMINATED = enum.auto()


class PodType(enum.Enum):
    INTERRUPTABLE = enum.auto()
    RESERVED = enum.auto()
    BID = enum.auto()
    BACKGROUND = enum.auto()


@dc.dataclass(frozen=True)
class PodRegistry:
    auth: String
    pass_: String
    url: String
    user: String
    username: String


@dc.dataclass(frozen=True)
class PodRuntime:
    container: 'PodRuntimeContainer'
    gpus: list['PodRuntimeGpus']
    ports: list['PodRuntimePorts']
    uptimeInSeconds: Int


@dc.dataclass(frozen=True)
class PodRuntimeContainer:
    cpuPercent: Int
    memoryPercent: Int


@dc.dataclass(frozen=True)
class PodRuntimeGpus:
    id: String
    gpuUtilPercent: Int
    memoryUtilPercent: Int


@dc.dataclass(frozen=True)
class PodRuntimePorts:
    ip: String
    isIpPublic: Boolean
    privatePort: Int
    publicPort: Int
    type: String


@dc.dataclass(frozen=True)
class PodMachineInfo:
    costPerHr: Float
    currentPricePerGpu: Float
    diskMBps: Int
    gpuAvailable: Int
    gpuDisplayName: String
    gpuTypeId: String
    gpuType: 'GpuType'
    listed: Boolean
    location: String
    maintenanceEnd: DateTime
    maintenanceNote: String
    maintenanceStart: DateTime
    maxDownloadSpeedMbps: Int
    maxUploadSpeedMbps: Int
    note: String
    podHostId: String
    secureCloud: Boolean
    supportPublicIp: Boolean


@dc.dataclass(frozen=True)
class GpuType:
    # lowestPrice: LowestPrice
    # input: GpuLowestPriceInput
    maxGpuCount: Int
    id: String
    displayName: String
    manufacturer: String
    memoryInGb: Int
    cudaCores: Int
    secureCloud: Boolean
    communityCloud: Boolean
    securePrice: Float
    communityPrice: Float
    oneMonthPrice: Float
    threeMonthPrice: Float
    oneWeekPrice: Float
    communitySpotPrice: Float
    secureSpotPrice: Float


@dc.dataclass(frozen=True)
class PodTelemetry:
    state: String
    time: DateTime
    cpuUtilization: Float
    memoryUtilization: Float
    averageGpuMetrics: 'GpuTelemetry'
    individualGpuMetrics: list['GpuTelemetry']
    lastStateTransitionTimestamp: Int


@dc.dataclass(frozen=True)
class GpuTelemetry:
    id: String
    percentUtilization: Float
    temperatureCelcius: Float
    memoryUtilization: Float
    powerWatts: Float


@dc.dataclass(frozen=True)
class Gpu:
    id: str
    podId: String
