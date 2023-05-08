from omlish import dataclasses as dc


@dc.dataclass(frozen=True)
class Dtype:
    name: str


Float32 = Dtype('float32')
