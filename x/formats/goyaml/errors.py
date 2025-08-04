import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')

YamlErrorOr = ta.Union['YamlError', T]  # ta.TypeAlias


##


@dc.dataclass(frozen=True)
class YamlError:
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
        return YamlError(obj)
    else:
        raise TypeError(obj)

