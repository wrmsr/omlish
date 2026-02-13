import dataclasses as dc


##


@dc.dataclass(frozen=True)
class PipelineHttpResponseHead:
    version: str
    status: int
    reason: str
    headers: dict[str, str]

    def header(self, name: str) -> str | None:
        return self.headers.get(name.casefold())
