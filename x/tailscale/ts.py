"""
https://github.com/tailscale/tailscale/blob/main/api.md

curl -su "$TAILSCALE_API_KEY:" https://api.tailscale.com/api/v2/tailnet/-/devices

==

https://www.reddit.com/r/Tailscale/comments/wk5bwm/how_do_i_login_to_tailscale_on_a_headless_ubuntu/
https://tailscale.com/kb/1085/auth-keys
"""
import datetime

from omlish import dataclasses as dc
from omlish import marshal as msh


@dc.dataclass(frozen=True)
class Device:
    dc.metadata(msh.ObjectMetadata(
        field_naming=msh.Naming.CAMEL,
        unknown_field='x',
    ))

    addresses: list[str]
    authorized: bool
    blocks_incoming_connections: bool
    client_version: str
    created: datetime.datetime
    expires: datetime.datetime
    hostname: str
    id: str
    is_external: bool
    key_expiry_disabled: bool
    last_seen: datetime.datetime
    machine_key: str
    name: str
    nodeId: str
    nodeKey: str
    os: str
    tailnet_lock_error: str
    tailnet_lock_key: str
    update_available: bool
    user: bool


def _main():
    pass


if __name__ == '__main__':
    _main()
