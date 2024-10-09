import subprocess
import sys
import typing as ta

from omdev.cli import CliModule
from omlish import argparse as ap
from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.CAMEL, source_field='x', ignore_unknown=True)
class Node:
    id: str = dc.xfield() | msh.update_field_metadata(name='ID')
    public_key: str = dc.xfield()
    host_name: str = dc.xfield()
    dns_name: str | None = dc.xfield(None) | msh.update_field_metadata(name='DNSName')
    tailscale_ips: ta.Sequence[str] | None = dc.xfield(None) | msh.update_field_metadata(name='TailscaleIPs')
    allowed_ips: ta.Sequence[str] | None = dc.xfield(None) | msh.update_field_metadata(name='AllowedPs')
    tags: ta.Sequence[str] | None = None

    x: ta.Mapping[str, ta.Any] | None = dc.xfield(None) | msh.update_field_metadata(no_marshal=True)


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.CAMEL, source_field='x', ignore_unknown=True)
class Status:
    version: str | None = None
    backend_state: str | None = None
    tailscale_ips: ta.Sequence[str] | None = dc.xfield(None) | msh.update_field_metadata(name='TailscaleIPs')
    self: Node | None = None
    peers: ta.Mapping[str, Node] | None = dc.xfield(None) | msh.update_field_metadata(name='Peer')

    @cached.property
    def nodes(self) -> ta.Sequence[Node]:
        return [
            *([self.self] if self.self is not None else []),
            *(self.peers.values() if self.peers else []),
        ]

    @cached.property
    def nodes_by_host_name(self) -> ta.Mapping[str, Node]:
        return col.make_map(((n.host_name, n) for n in self.nodes if n.host_name), strict=True)

    x: ta.Mapping[str, ta.Any] | None = dc.xfield(None) | msh.update_field_metadata(no_marshal=True)


class Cli(ap.Cli):
    @lang.cached_function
    def bin(self) -> str:
        if sys.platform == 'darwin':
            return '/Applications/Tailscale.app/Contents/MacOS/Tailscale'
        else:
            return 'tailscale'

    @ap.command(name='bin')
    def bin_cmd(self) -> None:
        print(self.bin())

    def status(self) -> Status:
        stdout = subprocess.check_output([
            self.bin(),
            'status',
            '--json',
        ])
        return msh.unmarshal(json.loads(stdout.decode()), Status)

    @ap.command(
        ap.arg('name'),
    )
    def ip(self) -> None:
        node = self.status().nodes_by_host_name[self.args.name]
        print(json.dumps_pretty(msh.marshal(node)))


# @omlish-manifest
_CLI_MODULE = CliModule(['tailscale', 'ts'], __name__)


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
