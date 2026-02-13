# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class PipelineHttpResponseHead:
    version: str
    status: int
    reason: str
    headers: ta.Mapping[str, str]

    def header(self, name: str) -> ta.Optional[str]:
        return self.headers.get(name.casefold())
