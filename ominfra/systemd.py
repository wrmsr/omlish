# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class SystemdListUnit:
    unit: str
    load: str  # loaded, not-found
    active: str  # active, inactive
    sub: str  # running, exited, dead
    description: str

    @classmethod
    def parse(cls, s: str) -> 'SystemdListUnit':
        return SystemdListUnit(*[p.strip() for p in s.strip().split(None, 4)])

    @classmethod
    def parse_all(cls, s: str) -> ta.List['SystemdListUnit']:
        return [
            cls.parse(sl)
            for l in s.strip().splitlines()
            if (sl := l.strip())
        ]


PARSABLE_SYSTEMD_LIST_UNIT_ARGS: ta.Sequence[str] = [
    '--all',
    '--no-legend',
    '--no-pager',
    '--plain',
]


##


def parse_systemd_show_output(s: str) -> ta.Mapping[str, str]:
    d: ta.Dict[str, str] = {}
    for l in s.strip().splitlines():
        if not (l := l.strip()):
            continue
        k, _, v = l.partition('=')
        d[k] = v
    return d
