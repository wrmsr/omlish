from omlish import dataclasses as dc
from omlish import lang

from .sequence import SequenceContent


##


@dc.dataclass(frozen=True)
class ContainerContent(SequenceContent, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class FlowContent(ContainerContent, lang.Final):
    """~Sentences"""


@dc.dataclass(frozen=True)
class ConcatContent(ContainerContent, lang.Final):
    """~Characters"""


@dc.dataclass(frozen=True)
class BlocksContent(ContainerContent, lang.Final):
    """~Paragraphs"""
