from .. import docker
from .. import marshal as msh
from ..formats import json
from ..testing import pytest as ptu


@ptu.skip_if_not_on_path('docker')
def test_docker():
    pis = docker.cli_ps()
    print(json.dumps_pretty(msh.marshal(pis, list[docker.PsItem])))
    print(json.dumps_pretty(msh.marshal(pis)))

    iis = docker.cli_inspect([pi.id for pi in pis])
    print(json.dumps_pretty(msh.marshal(iis, list[docker.Inspect])))
