# ruff: noqa: UP006 UP007
# @omlish-lite
import typing as ta


class HttpProtocolVersion(ta.NamedTuple):
    major: int
    minor: int

    def __str__(self) -> str:
        return f'HTTP/{self.major}.{self.minor}'


class HttpProtocolVersions:
    HTTP_0_9 = HttpProtocolVersion(0, 9)
    HTTP_1_0 = HttpProtocolVersion(1, 0)
    HTTP_1_1 = HttpProtocolVersion(1, 1)
    HTTP_2_0 = HttpProtocolVersion(2, 0)
