from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class PrintingConfig:
    markdown: bool = False
