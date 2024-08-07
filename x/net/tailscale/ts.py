"""
https://github.com/tailscale/tailscale/blob/main/api.md

curl -su "$TAILSCALE_API_KEY:" https://api.tailscale.com/api/v2/tailnet/-/devices

==

https://www.reddit.com/r/Tailscale/comments/wk5bwm/how_do_i_login_to_tailscale_on_a_headless_ubuntu/
https://tailscale.com/kb/1085/auth-keys

==

curl -fsSL https://tailscale.com/install.sh | sh

tailscale up --authkey=tskey-0123456789abcdef --hostname=server-foo
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


@dc.dataclass(frozen=True)
class CreatedKey:
    dc.metadata(msh.ObjectMetadata(
        field_naming=msh.Naming.LOW_CAMEL,
        unknown_field='x',
    ))

    id: str
    key: str
    created: datetime.datetime
    expires: datetime.datetime
    capabilities: ta.Mapping[str, ta.Any]
    description: str

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True)
class ListedKey:
    dc.metadata(msh.ObjectMetadata(
        field_naming=msh.Naming.LOW_CAMEL,
        unknown_field='x',
    ))

    id: str
    description: str

    x: ta.Mapping[str, ta.Any] | None = None


def _main():
    sec = load_secrets()
    auth = {'Authorization': hu.consts.format_basic_auth_header(sec['tailscale_api_key'], '').decode()}
    hdrs = {
        **auth,
        # hu.consts.HEADER_AUTH.decode(): hu.consts.CONTENT_TYPE_JSON_UTF8.decode(),
        # hu.consts.HEADER_ACCEPT.decode(): hu.consts.CONTENT_TYPE_JSON,
    }
    base_url = 'https://api.tailscale.com/api/v2'

    with urllib.request.urlopen(urllib.request.Request(
            f'{base_url}/tailnet/-/devices',
            headers=hdrs,
    )) as resp:
        buf = resp.read()

    dct = json.loads(buf.decode())
    devs = msh.unmarshal(dct['devices'], list[Device])
    print(devs)

    with urllib.request.urlopen(urllib.request.Request(
            f'{base_url}/tailnet/-/keys',
            method='POST',
            headers=hdrs,
            data=json.dumps({
                'capabilities': {
                    'devices': {
                        'create': {
                            'reusable': False,
                            'ephemeral': True,
                            'preauthorized': True,
                            'tags': [
                                'tag:infra',
                            ]
                        }
                    }
                },
                'expirySeconds': 3600,
                'description': 'infra access',
            }).encode(),
    )) as resp:
        buf = resp.read()

    dct = json.loads(buf.decode())
    print(dct)

    with urllib.request.urlopen(urllib.request.Request(
            f'{base_url}/tailnet/-/keys',
            headers=hdrs,
    )) as resp:
        buf = resp.read()

    dct = json.loads(buf.decode())
    print(dct)



if __name__ == '__main__':
    _main()
