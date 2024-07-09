import dataclasses as dc
import subprocess


@dc.dataclass(frozen=True)
class PsItem:
    pid: int
    ppid: int
    exe: str


def get_ps_item(pid: int) -> PsItem: