"""
https://peps.python.org/pep-0249/
"""
import enum
import typing as ta


##


DbapiTypeCode: ta.TypeAlias = ta.Any | None

DbapiColumnDescription: ta.TypeAlias = tuple[
    str,  # name
    DbapiTypeCode,  # type_code
    int | None,  # display_size
    int | None,  # internal_size
    int | None,  # precision
    int | None,  # scale
    bool | None,  # null_ok
]


class DbapiColumnDescription_(ta.NamedTuple):  # noqa
    name: str
    type_code: DbapiTypeCode
    display_size: int | None
    internal_size: int | None
    precision: int | None
    scale: int | None
    null_ok: bool | None

    @classmethod
    def of(cls, obj: ta.Any) -> 'DbapiColumnDescription_':
        if isinstance(obj, cls):
            return obj
        else:
            return cls(*obj[:len(cls._fields)])


class DbapiConnection(ta.Protocol):
    def close(self) -> object: ...

    def commit(self) -> object: ...

    # optional:
    # def rollback(self) -> ta.Any: ...

    def cursor(self) -> 'DbapiCursor': ...


class DbapiCursor(ta.Protocol):
    @property
    def description(self) -> ta.Sequence[DbapiColumnDescription] | None: ...

    @property
    def rowcount(self) -> int: ...

    # optional:
    # def callproc(self, procname: str, parameters: Sequence[ta.Any] = ...) -> Sequence[ta.Any]: ...

    def close(self) -> object: ...

    def execute(
        self,
        operation: str,
        parameters: ta.Sequence[ta.Any] | ta.Mapping[str, ta.Any] = ...,
    ) -> object: ...

    def executemany(
        self,
        operation: str,
        seq_of_parameters: ta.Sequence[ta.Sequence[ta.Any]],
    ) -> object: ...

    def fetchone(self) -> ta.Sequence[ta.Any] | None: ...

    def fetchmany(self, size: int = ...) -> ta.Sequence[ta.Sequence[ta.Any]]: ...

    def fetchall(self) -> ta.Sequence[ta.Sequence[ta.Any]]: ...

    # optional:
    # def nextset(self) -> None | Literal[True]: ...

    arraysize: int

    def setinputsizes(self, sizes: ta.Sequence[DbapiTypeCode | int | None]) -> object: ...

    def setoutputsize(self, size: int, column: int = ...) -> object: ...


class DbapiThreadSafety(enum.IntEnum):
    NONE = 0
    MODULE = 1
    CONNECTION = 2
    CURSOR = 3


class DbapiModule(ta.Protocol):
    def connect(self, *args: ta.Any, **kwargs: ta.Any) -> DbapiConnection: ...

    #

    @property
    def apilevel(self) -> str: ...

    @property
    def threadsafety(self) -> int: ...

    @property
    def paramstyle(self) -> str: ...

    #

    @property
    def Warning(self) -> type[Exception]: ...  # noqa

    @property
    def Error(self) -> type[Exception]: ...  # noqa

    @property
    def InterfaceError(self) -> type[Exception]: ...  # noqa

    @property
    def DatabaseError(self) -> type[Exception]: ...  # noqa

    @property
    def DataError(self) -> type[Exception]: ...  # noqa

    @property
    def OperationalError(self) -> type[Exception]: ...  # noqa

    @property
    def IntegrityError(self) -> type[Exception]: ...  # noqa

    @property
    def InternalError(self) -> type[Exception]: ...  # noqa

    @property
    def ProgrammingError(self) -> type[Exception]: ...  # noqa

    @property
    def NotSupportedError(self) -> type[Exception]: ...  # noqa

    #

    def Date(self, year: ta.Any, month: ta.Any, day: ta.Any) -> ta.Any: ...  # noqa

    def Time(self, hour: ta.Any, minute: ta.Any, second: ta.Any) -> ta.Any: ...  # noqa

    def Timestamp(self, year, month, day, hour, minute, second) -> ta.Any: ...  # noqa

    def DateFromTicks(self, ticks: ta.Any) -> ta.Any: ...  # noqa

    def TimeFromTicks(self, ticks: ta.Any) -> ta.Any: ...  # noqa

    def TimestampFromTicks(self, ticks: ta.Any) -> ta.Any: ...  # noqa

    def Binary(self, string: ta.Any) -> ta.Any: ...  # noqa

    @property
    def STRING(self) -> type: ...  # noqa

    @property
    def BINARY(self) -> type: ...  # noqa

    @property
    def NUMBER(self) -> type: ...  # noqa

    @property
    def DATETIME(self) -> type: ...  # noqa

    @property
    def ROWID(self) -> type: ...  # noqa
