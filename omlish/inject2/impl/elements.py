import typing as ta

from ... import lang
from ..elements import Element


class ElementCollection(lang.Final):
    def __init__(self, es: ta.Iterable[Element]) -> None:
        super().__init__()

        lst = list(es)
