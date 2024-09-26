from ... import marshal as msh
from ...diag.pydevd import silence_subprocess_check
from ...formats import json
from ...testing import pytest as ptu
from .. import cli


@ptu.skip.if_not_on_path('docker')
def test_cli():
    silence_subprocess_check()

    pis = cli.cli_ps()
    print(json.dumps_pretty(msh.marshal(pis, list[cli.PsItem])))
    print(json.dumps_pretty(msh.marshal(pis)))

    iis = cli.cli_inspect([pi.id for pi in pis])
    print(json.dumps_pretty(msh.marshal(iis, list[cli.Inspect])))
