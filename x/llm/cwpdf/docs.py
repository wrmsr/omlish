import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Doc:
    content: str
    metadata: ta.Mapping[str, ta.Any] | None = None
    id: str | None = None


class DocAndScore(ta.NamedTuple):
    doc: Doc
    score: float
