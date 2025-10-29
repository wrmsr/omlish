# ruff: noqa: UP007
# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract


T = ta.TypeVar('T')

YamlErrorOr = ta.Union['YamlError', T]  # ta.TypeAlias


##


class YamlError(Abstract):
    @property
    @abc.abstractmethod
    def message(self) -> str:
        raise NotImplementedError


class EofYamlError(YamlError):
    @property
    def message(self) -> str:
        return 'eof'


@dc.dataclass(frozen=True)
class GenericYamlError(YamlError):
    obj: ta.Union[str, Exception]

    @property
    def message(self) -> str:
        if isinstance(self.obj, str):
            return self.obj
        else:
            return str(self.obj)


def yaml_error(obj: ta.Union[YamlError, str, Exception]) -> YamlError:
    if isinstance(obj, YamlError):
        return obj
    elif isinstance(obj, (str, Exception)):
        return GenericYamlError(obj)
    else:
        raise TypeError(obj)
