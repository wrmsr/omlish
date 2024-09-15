import pytest

from .. import docker
from .. import marshal as msh
from ..diag.pydevd import silence_subprocess_check
from ..formats import json
from ..testing import pytest as ptu


@ptu.skip_if_not_on_path('docker')
def test_docker():
    silence_subprocess_check()

    pis = docker.cli_ps()
    print(json.dumps_pretty(msh.marshal(pis, list[docker.PsItem])))
    print(json.dumps_pretty(msh.marshal(pis)))

    iis = docker.cli_inspect([pi.id for pi in pis])
    print(json.dumps_pretty(msh.marshal(iis, list[docker.Inspect])))


@pytest.mark.online
def test_hub_image_version():
    repo = 'library/nginx'
    info = docker.get_hub_repo_info(repo)
    assert info.tags
    assert info.latest_manifests
