from ...subprocesses.sync import subprocesses
from ...testing import pytest as ptu
from .. import ns1


@ptu.skip.if_not_platform('darwin')
def test_list_used_tcp_ports() -> None:
    ps = ns1.DockerNs1ListUsedTcpPortsCommand().run(subprocesses)
    assert all(isinstance(p, int) for p in ps)
