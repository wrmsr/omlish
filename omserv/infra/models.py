from omlish import dataclasses as dc


@dc.dataclass(frozen=True)
class Server:
    host: str
