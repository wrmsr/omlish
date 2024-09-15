import abc
import dataclasses as dc
import enum
import typing as ta

from omlish import collections as col
from omlish import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')


#


@dc.dataclass(frozen=True)
class Prompt(lang.Final):
    s: str


