"""
Pod
lowestBidPriceToResume - Float
aiApiId - String
apiKey - String
consumerUserId - String
containerDiskInGb - Int
containerRegistryAuthId - String
costMultiplier - Float
costPerHr - Float!
adjustedCostPerHr - Float!
desiredStatus - PodStatus!
dockerArgs - String
dockerId - String
env - [String]
gpuCount - Int!
gpuPowerLimitPercent - Int!
gpus - [Gpu]!
id - String!
imageName - String!
lastStatusChange - String
locked - Boolean
machineId - String!
memoryInGb - Float!
name - String!
podType - PodType
port - Port
ports - String
registry - PodRegistry
templateId - String
uptimeSeconds - Int
vcpuCount - Float!
version - Int
volumeEncrypted - Boolean!
volumeInGb - Float
volumeKey - String
volumeMountPath - String
runtime - PodRuntime
machine - PodMachineInfo
latestTelemetry - PodTelemetry
# endpoint - Endpoint
# networkVolume - NetworkVolume
# savingsPlans - [SavingsPlan]

PodStatus
CREATED
RUNNING
RESTARTING
EXITED
PAUSED
DEAD
TERMINATED

PodType
INTERRUPTABLE
RESERVED
BID
BACKGROUND

PodRegistry
auth - String
pass - String
url - String
user - String
username - String

PodRuntime
container - PodRuntimeContainer
gpus - [PodRuntimeGpus]
ports - [PodRuntimePorts]
uptimeInSeconds - Int

PodRuntimeContainer
cpuPercent - Int
memoryPercent - Int

PodRuntimeGpus
id - String
gpuUtilPercent - Int
memoryUtilPercent - Int

PodRuntimePorts
ip - String
isIpPublic - Boolean
privatePort - Int
publicPort - Int
type - String

PodMachineInfo
costPerHr - Float
currentPricePerGpu - Float
diskMBps - Int
gpuAvailable - Int
gpuDisplayName - String
gpuTypeId - String
gpuType - GpuType
listed - Boolean
location - String
maintenanceEnd - DateTime
maintenanceNote - String
maintenanceStart - DateTime
maxDownloadSpeedMbps - Int
maxUploadSpeedMbps - Int
note - String
podHostId - String
secureCloud - Boolean
supportPublicIp - Boolean

GpuType
lowestPrice - LowestPrice
input - GpuLowestPriceInput
maxGpuCount - Int
id - String
displayName - String
manufacturer - String
memoryInGb - Int
cudaCores - Int
secureCloud - Boolean
communityCloud - Boolean
securePrice - Float
communityPrice - Float
oneMonthPrice - Float
threeMonthPrice - Float
oneWeekPrice - Float
communitySpotPrice - Float
secureSpotPrice - Float

PodTelemetry
state - String
time - DateTime
cpuUtilization - Float
memoryUtilization - Float
averageGpuMetrics - GpuTelemetry
individualGpuMetrics - [GpuTelemetry]
lastStateTransitionTimestamp - Int

GpuTelemetry
id - String
percentUtilization - Float
temperatureCelcius - Float
memoryUtilization - Float
powerWatts - Float
"""
