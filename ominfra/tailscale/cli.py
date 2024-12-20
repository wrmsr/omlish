import re
import subprocess
import sys
import typing as ta

from omdev.cli import CliModule
from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.formats import json


##


_IP_V4_PAT = re.compile(r'\d{1,3}(\.\d{1,3}){3}')


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.CAMEL, unknown_field='x')
class CliNode:
    id: str = dc.xfield() | msh.update_field_metadata(name='ID')
    public_key: str = dc.xfield()
    host_name: str = dc.xfield()
    dns_name: str | None = dc.xfield(None) | msh.update_field_metadata(name='DNSName')
    tailscale_ips: ta.Sequence[str] | None = dc.xfield(None) | msh.update_field_metadata(name='TailscaleIPs')
    allowed_ips: ta.Sequence[str] | None = dc.xfield(None) | msh.update_field_metadata(name='AllowedPs')
    tags: ta.Sequence[str] | None = None

    @property
    def ipv4s(self) -> ta.Sequence[str]:
        return [i for i in self.tailscale_ips or () if _IP_V4_PAT.fullmatch(i)]

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.CAMEL, unknown_field='x')
class CliStatus:
    version: str | None = None
    backend_state: str | None = None
    tailscale_ips: ta.Sequence[str] | None = dc.xfield(None) | msh.update_field_metadata(name='TailscaleIPs')
    self: CliNode | None = None
    peers: ta.Mapping[str, CliNode] | None = dc.xfield(None) | msh.update_field_metadata(name='Peer')

    @cached.property
    def nodes(self) -> ta.Sequence[CliNode]:
        return [
            *([self.self] if self.self is not None else []),
            *(self.peers.values() if self.peers else []),
        ]

    @cached.property
    def nodes_by_host_name(self) -> ta.Mapping[str, CliNode]:
        return col.make_map(((n.host_name, n) for n in self.nodes if n.host_name), strict=True)

    x: ta.Mapping[str, ta.Any] | None = None


##


class Cli(ap.Cli):
    @lang.cached_function
    def bin(self) -> str:
        if sys.platform == 'darwin':
            return '/Applications/Tailscale.app/Contents/MacOS/Tailscale'
        else:
            return 'tailscale'

    @ap.cmd(name='bin')
    def bin_cmd(self) -> None:
        print(self.bin())

    def status(self) -> CliStatus:
        stdout = subprocess.check_output([
            self.bin(),
            'status',
            '--json',
        ])
        return msh.unmarshal(json.loads(stdout.decode()), CliStatus)

    @ap.cmd(
        ap.arg('name', nargs='?'),
        name='status',
    )
    def status_cmd(self) -> None:
        status = self.status()
        out: ta.Any
        if (name := self.args.name):
            out = status.nodes_by_host_name[name]
        else:
            out = status
        print(json.dumps_pretty(msh.marshal(out)))

    @ap.cmd()
    def ips(self) -> None:
        print(json.dumps_pretty({
            hn: node.ipv4s
            for hn, node in self.status().nodes_by_host_name.items()
        }))

    @ap.cmd(
        ap.arg('name', nargs='?'),
    )
    def ip(self) -> None:
        status = self.status()
        if self.args.name:
            print(status.nodes_by_host_name[self.args.name].ipv4s[0])
        else:
            print(check.not_none(status.self).ipv4s[0])


# @omlish-manifest
_CLI_MODULE = CliModule(['tailscale', 'ts'], __name__)


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
