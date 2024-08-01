"""
https://github.com/tailscale/tailscale/blob/main/api.md

curl -su "$TAILSCALE_API_KEY:" https://api.tailscale.com/api/v2/tailnet/-/devices

==

https://www.reddit.com/r/Tailscale/comments/wk5bwm/how_do_i_login_to_tailscale_on_a_headless_ubuntu/
https://tailscale.com/kb/1085/auth-keys
"""
import datetime
import json
import urllib.request
import typing as ta

from omlish import dataclasses as dc
from omlish import http as hu
from omlish import marshal as msh
from omserv.secrets import load_secrets


@dc.dataclass(frozen=True)
class Device:
    dc.metadata(msh.ObjectMetadata(
        field_naming=msh.Naming.LOW_CAMEL,
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
    node_id: str
    node_key: str
    os: str
    tailnet_lock_error: str
    tailnet_lock_key: str
    update_available: bool
    user: bool

    x: ta.Mapping[str, ta.Any] | None = None


def _main():
    sec = load_secrets()

    url = 'https://api.tailscale.com/api/v2/tailnet/-/devices'

    request = urllib.request.Request(url)
    request.add_header('Authorization', hu.consts.format_basic_auth_header(sec['tailscale_api_key'], '').decode())
    with urllib.request.urlopen(request) as resp:
        buf = resp.read()
    dct = json.loads(buf.decode())
    devs = msh.unmarshal(dct['devices'], list[Device])
    print(devs)


if __name__ == '__main__':
    _main()
