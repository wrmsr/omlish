import datetime
import subprocess
import typing as ta  # noqa

from omlish import dataclasses as dc

from ... import marshal as msh


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
    command: str        # `json:"Command"`
    created_at: str     # `json:"CreatedAt"`
    id: str             # `json:"ID"`
    image: str          # `json:"Image"`
    labels: str         # `json:"Labels"`
    local_volumes: str  # `json:"LocalVolumes"`
    mounts: str         # `json:"Mounts"`
    names: str          # `json:"Names"`
    networks: str       # `json:"Networks"`
    ports: str          # `json:"Ports"`
    running_for: str    # `json:"RunningFor"`
    size: str           # `json:"Size"`
    state: str          # `json:"State"`
    status: str         # `json:"Status"`

    # x: dict[str, ta.Any]  # `json:"-"`


def test_docker():
    out, err = subprocess.Popen(['docker', 'ps', '--format', '{{json .}}']).communicate()
    print(out)

    # reg = msh.Registry()
    # uf = msh.new_standard_unmarshaler_factory()
    # uc = msh.UnmarshalContext(registry=reg, factory=uf)
    # uobj = uc.make(Ps).unmarshal(uc, mobj)
