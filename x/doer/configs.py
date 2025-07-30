# ruff: noqa: UP006 UP007 UP043 UP045
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check


##


@dc.dataclass(frozen=True)
class DoerConfig:
    consts: ta.Any = None  # ta.Union[ta.Mapping[str, ta.Any], ta.Sequence[ta.Mapping[str, ta.Any]], None] = None

    @cached_nullary
    def consts_ns(self) -> ta.Mapping[str, ta.Any]:
        if not self.consts:
            return {}
        elif isinstance(self.consts, ta.Mapping):
            return self.consts
        elif isinstance(self.consts, ta.Sequence):
            ns = {}
            for m in self.consts:
                for k, v in check.isinstance(m, ta.Mapping).items():
                    if k in ns:
                        raise KeyError(k)
                    ns[k] = v
            return ns
        else:
            raise TypeError(self.consts)

    @dc.dataclass(frozen=True)
    class Shell:
        env: ta.Optional[ta.Mapping[str, str]] = None

        preamble: ta.Union[str, ta.Sequence[str], None] = None

        @cached_nullary
        def joined_preamble(self) -> ta.Optional[str]:
            if self.preamble is None:
                return None
            elif isinstance(self.preamble, str):
                return self.preamble
            elif isinstance(self.preamble, ta.Sequence):
                return '\n'.join(self.preamble)
            else:
                raise TypeError(self.preamble)

    shell: Shell = Shell()


##


@dc.dataclass(frozen=True)
class DoerExecutableConfig(abc.ABC):  # noqa
    name: ta.Optional[str] = None

    # timeout: ta.Optional[float] = None  # FIXME


@dc.dataclass(frozen=True)
class ShellDoerExecutableConfig(DoerExecutableConfig, abc.ABC):
    sh: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class PythonDoerExecutableConfig(DoerExecutableConfig, abc.ABC):
    py: ta.Optional[str] = None


##


@dc.dataclass(frozen=True)
class DoerTaskArg:
    name: ta.Union[str, ta.Sequence[str], None] = None
    type: ta.Literal['int', 'float', 'bool', None] = None
    nargs: ta.Literal['?', '+', '*', None] = None
    default: ta.Optional[ta.Any] = None


@dc.dataclass(frozen=True)
class DoerTaskConfig(DoerExecutableConfig, abc.ABC):
    args: ta.Optional[ta.Sequence[DoerTaskArg]] = None
    # accepts_unknown_args: ta.Optional[bool] = None  # FIXME


@dc.dataclass(frozen=True)
class ShellDoerTaskConfig(DoerTaskConfig, ShellDoerExecutableConfig):
    pass


@dc.dataclass(frozen=True)
class PythonDoerTaskConfig(DoerTaskConfig, PythonDoerExecutableConfig):
    pass


##


@dc.dataclass(frozen=True)
class DoerDefConfig(DoerExecutableConfig, abc.ABC):
    params: ta.Union[str, ta.Sequence[str], None] = None

    cache: ta.Union[bool, int, None] = None


@dc.dataclass(frozen=True)
class ShellDoerDefConfig(DoerDefConfig, ShellDoerExecutableConfig):
    preserve_trailing_newlines: ta.Optional[bool] = None


@dc.dataclass(frozen=True)
class PythonDoerDefConfig(DoerDefConfig, PythonDoerExecutableConfig):
    pass
