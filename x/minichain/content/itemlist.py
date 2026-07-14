import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .sequence import SequenceContent


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ItemListContent(SequenceContent, lang.Final):
    _: dc.KW_ONLY

    style: ta.Literal['-', '#'] = '-'
