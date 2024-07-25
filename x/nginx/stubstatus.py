import dataclasses as dc
import textwrap
import typing as ta


@dc.dataclass(frozen=True, kw_only=True)
class StubStatus:
    active: int
    counts: ta.Mapping[str, int]
    reading: int
    writing: int
    waiting: int


def parse_stub_status(s: str) -> StubStatus:
    lines = s.strip().splitlines()
    raise NotImplementedError


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
