"""
https://github.com/tailscale/tailscale/blob/main/api.md

curl -su "$TAILSCALE_API_KEY:" https://api.tailscale.com/api/v2/tailnet/-/devices
"""
import datetime

from omlish import dataclasses as dc


@dc.dataclass(frozen=True)
class Device:
    addresses: list[str]
    authorized: bool
    blocksIncomingConnections: bool
    clientVersion: str
    created: datetime.datetime
    expires: datetime.datetime
    hostname: str
    id: str
    isExternal: bool
    keyExpiryDisabled: bool
    lastSeen: datetime.datetime
    machineKey: str
    name: str
    nodeId: str
    nodeKey: str
    os: str
    tailnetLockError: str
    tailnetLockKey: str
    updateAvailable: bool
    user: bool
