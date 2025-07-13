import dataclasses as dc
import re
import textwrap
import typing as ta


##


@dc.dataclass(frozen=True, kw_only=True)
class StubStatus:
    active: int

    # std: accepts handled requests
    # ext: 2xx 4xx 5xx
    counts: ta.Mapping[str, int]

    reading: int
    writing: int
    waiting: int


_ACTIVE_PAT = re.compile(r'^Active connections: (?P<active>\d+)')
_RWW_PAT = re.compile(r'^Reading: (?P<reading>\d+) Writing: (?P<writing>\d+) Waiting: (?P<waiting>\d+)')


def parse_stub_status(s: str) -> StubStatus:
    # Active connections: 1
    # server accepts handled requests 2xx 4xx 5xx
    #  20 20 20 18 1 0
    # Reading: 0 Writing: 1 Waiting: 0

    lines = [l for l in s.splitlines() for l in [l.strip()] if l]
    if len(lines) < 4:
        raise Exception('Not enough lines')

    if (active_m := _ACTIVE_PAT.match(lines[0])) is None:
        raise Exception('Failed to match active line')
    active = int(active_m.groupdict()['active'])

    if (rww_m := _RWW_PAT.match(lines[3])) is None:
        raise Exception('Failed to match rww line')
    reading = int(rww_m.groupdict()['reading'])
    writing = int(rww_m.groupdict()['writing'])
    waiting = int(rww_m.groupdict()['waiting'])

    ct_lbl = lines[1].split()[1:]
    ct_val = lines[2].split()
    if len(ct_lbl) != len(ct_val):
        raise Exception('Counts label/value mismatch')
    counts = {l: int(v) for l, v in zip(ct_lbl, ct_val)}

    return StubStatus(
        active=active,

        counts=counts,

        reading=reading,
        writing=writing,
        waiting=waiting,
    )


def _main() -> None:
    s = textwrap.dedent("""
        Active connections: 1
        server accepts handled requests 2xx 4xx 5xx
         20 20 20 18 1 0
        Reading: 0 Writing: 1 Waiting: 0
    """)
    ss = parse_stub_status(s)
    print(ss)


if __name__ == '__main__':
    _main()
