import datetime
import json
import subprocess
import typing as ta  # noqa

from omlish import dataclasses as dc
from omlish import marshal as msh
import pytest


@dc.dataclass()
class InspectState:
    status: str       # `json:"Status"`
    running: bool     # `json:"Running"`
    paused: bool      # `json:"Paused"`
    restarting: bool  # `json:"Restarting"`
    oom_killed: bool  # `json:"OOMKilled"`
    dead: bool        # `json:"Dead"`
    pid: int          # `json:"Pid"`
    exit_code: int    # `json:"ExitCode"`
    error: str        # `json:"Error"`

    started_at: datetime.datetime   # `json:"StartedAt"`
    finished_at: datetime.datetime  # `json:"FinishedAt"`

    # x dict[str, ta.Any] #  `json:"-"`


@dc.dataclass()
class Ps:
    command: str = dc.field(metadata={msh.Field: msh.Field(name='Command')})
    created_at: str = dc.field(metadata={msh.Field: msh.Field(name='CreatedAt')})
    id: str = dc.field(metadata={msh.Field: msh.Field(name='ID')})
    image: str = dc.field(metadata={msh.Field: msh.Field(name='Image')})
    labels: str = dc.field(metadata={msh.Field: msh.Field(name='Labels')})
    local_volumes: str = dc.field(metadata={msh.Field: msh.Field(name='LocalVolumes')})
    mounts: str = dc.field(metadata={msh.Field: msh.Field(name='Mounts')})
    names: str = dc.field(metadata={msh.Field: msh.Field(name='Names')})
    networks: str = dc.field(metadata={msh.Field: msh.Field(name='Networks')})
    ports: str = dc.field(metadata={msh.Field: msh.Field(name='Ports')})
    running_for: str = dc.field(metadata={msh.Field: msh.Field(name='RunningFor')})
    size: str = dc.field(metadata={msh.Field: msh.Field(name='Size')})
    state: str = dc.field(metadata={msh.Field: msh.Field(name='State')})
    status: str = dc.field(metadata={msh.Field: msh.Field(name='Status')})

    # x: dict[str, ta.Any]  # `json:"-"`


def test_docker():
    out, err = subprocess.Popen([
        'docker',
        'ps',
        '--no-trunc',
        '--format', '{{json .}}',
    ], stdout=subprocess.PIPE).communicate()
    buf = out.decode('utf-8')
    if buf.startswith('Cannot connect to the Docker daemon at '):
        pytest.skip('docker not running')
    dct = json.loads(buf)
    print(dct)

    reg = msh.Registry()
    uf = msh.new_standard_unmarshaler_factory()
    uc = msh.UnmarshalContext(registry=reg, factory=uf)
    ps = uc.make(Ps).unmarshal(uc, dct)
    print(ps)
