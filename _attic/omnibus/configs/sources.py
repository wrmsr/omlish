import abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .configs import Config  # noqa


T = ta.TypeVar('T')
ConfigT = ta.TypeVar('ConfigT', bound='Config')


class FieldSource(lang.Abstract):

    @abc.abstractmethod
    def get(self, cls: ta.Type[ConfigT], field: dc.Field) -> ta.Any:
        raise NotImplementedError


class EmptyFieldSource(FieldSource):

    def get(self, cls: ta.Type[ConfigT], field: dc.Field) -> ta.Any:
        return dc.MISSING


class CompositeFieldSource(FieldSource):

    def __init__(self, *children: FieldSource) -> None:
        super().__init__()

        self._children = children

    def get(self, cls: ta.Type[ConfigT], field: dc.Field) -> ta.Any:
        for child in self._children:
            value = child.get(cls, field)
            if value is not dc.MISSING:
                return value
        return dc.MISSING


class DictFieldSource(FieldSource):

    def __init__(self, dct: ta.Mapping[str, ta.Any]) -> None:
        super().__init__()

        self._dct = check.not_none(dct)

    def get(self, cls: ta.Type[ConfigT], field: dc.Field) -> ta.Any:
        return self._dct.get(field.name, dc.MISSING)


class ConfigSource(lang.Abstract):

    @abc.abstractmethod
    def get(self, cls: ta.Type[ConfigT]) -> ConfigT:
        raise NotImplementedError
