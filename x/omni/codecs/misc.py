import typing as ta

from .. import defs
from .registries import EXTENSION_REGISTRY
from .types import Codec


@EXTENSION_REGISTRY.registering('lines')
class LinesCodec(Codec[ta.Iterable[str], str]):

    defs.repr()

    def encode(self, o: ta.Iterable[str]) -> str:
        return '\n'.join(o)

    def decode(self, o: str) -> ta.Iterable[str]:
        return o.split('\n')


lines = LinesCodec
