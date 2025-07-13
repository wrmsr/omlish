import datetime
import typing as ta

from omlish import dataclasses as dc
from omlish import marshal as msh


##


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
