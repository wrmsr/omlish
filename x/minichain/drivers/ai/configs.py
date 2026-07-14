from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class AiConfig:
    stream: bool = False

    enable_tools: bool = False
