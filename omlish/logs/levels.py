# ruff: noqa: UP006 UP045
# @omlish-lite
import logging
import typing as ta


LogLevel = int  # ta.TypeAlias


##


@ta.final
class NamedLogLevel(int):
    # logging.getLevelNamesMapping (or, as that is unavailable <3.11, logging._nameToLevel) includes the deprecated
    # aliases.
    _NAMES_BY_INT: ta.ClassVar[ta.Mapping[LogLevel, str]] = dict(sorted(logging._levelToName.items(), key=lambda t: -t[0]))  # noqa

    _INTS_BY_NAME: ta.ClassVar[ta.Mapping[str, LogLevel]] = {v: k for k, v in _NAMES_BY_INT.items()}

    _NAME_INT_PAIRS: ta.ClassVar[ta.Sequence[ta.Tuple[str, LogLevel]]] = list(_INTS_BY_NAME.items())

    #

    @ta.overload
    def __new__(cls, name: str) -> 'NamedLogLevel':
        ...

    @ta.overload
    def __new__(cls, i: int) -> 'NamedLogLevel':
        ...

    def __new__(cls, o):
        if isinstance(o, str):
            return cls(cls._INTS_BY_NAME[o.upper()])
        else:
            return super().__new__(cls, o)

    #

    @property
    def exact_name(self) -> ta.Optional[str]:
        return self._NAMES_BY_INT.get(self)

    _effective_name: ta.Optional[str]

    @property
    def effective_name(self) -> ta.Optional[str]:
        try:
            return self._effective_name
        except AttributeError:
            pass

        if (n := self.exact_name) is None:
            for n, i in self._NAME_INT_PAIRS:  # noqa
                if self >= i:
                    break
            else:
                n = None

        self._effective_name = n
        return n

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({int(self)})'

    def __str__(self) -> str:
        return self.exact_name or f'{self.effective_name or "INVALID"}:{int(self)}'

    #

    CRITICAL: ta.ClassVar['NamedLogLevel']
    ERROR: ta.ClassVar['NamedLogLevel']
    WARNING: ta.ClassVar['NamedLogLevel']
    INFO: ta.ClassVar['NamedLogLevel']
    DEBUG: ta.ClassVar['NamedLogLevel']
    NOTSET: ta.ClassVar['NamedLogLevel']


NamedLogLevel.CRITICAL = NamedLogLevel(logging.CRITICAL)
NamedLogLevel.ERROR = NamedLogLevel(logging.ERROR)
NamedLogLevel.WARNING = NamedLogLevel(logging.WARNING)
NamedLogLevel.INFO = NamedLogLevel(logging.INFO)
NamedLogLevel.DEBUG = NamedLogLevel(logging.DEBUG)
NamedLogLevel.NOTSET = NamedLogLevel(logging.NOTSET)
